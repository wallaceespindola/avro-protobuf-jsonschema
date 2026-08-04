![Banner](banner.png)

# Beyond JSON: What Avro and Protobuf Bring to Enterprise Data Contracts

**By Wallace Espindola**
Senior Software Engineer / Solution Architect
wallace.espindola@gmail.com | [LinkedIn](https://www.linkedin.com/in/wallaceespindola/) | [GitHub](https://github.com/wallaceespindola/)

---

## Abstract

Most Java shops standardize on JSON for everything, and for a long time that's a reasonable default. But once you're running dozens of services, streaming events through Kafka, or maintaining contracts that need to survive years of schema changes, JSON's looseness starts to cost you. This article walks through where Apache Avro and Protocol Buffers earn their keep in a Java enterprise stack, how their schemas map to real JVM code (`protoc`-generated classes, Avro `SpecificRecord` and `GenericRecord`), and how they fit alongside JSON Schema at the boundaries where humans and browsers are involved. Every schema and code example here comes from a working companion repository, so you can run the comparisons yourself rather than take my word for it. You'll come away with a concrete decision framework for choosing a serialization format per boundary, plus the Java patterns — Kafka producers with Confluent Schema Registry, gRPC services in Spring, Jackson-based JSON Schema validation — that make each format production-ready.

---

## Introduction

Here's a scenario I've walked into more than once: a team built their whole platform on JSON over REST, it worked fine for a year, and then two things happened at the same time. First, an internal service-to-service call started showing up on the latency dashboard, because the payload was a few hundred fields deep and JSON parsing wasn't free. Second, a data engineering team asked for a stable event feed out of the same system, and "stable" turned out to mean something very different to them than it did to the API team. JSON hadn't failed exactly, but it had been asked to do three jobs at once: human-readable API contract, high-throughput internal transport, and long-lived data pipeline format. It's not great at all three simultaneously.

That's the problem this article is about. Binary serialization formats like Avro and Protocol Buffers exist because different boundaries in your system need different things from a data contract. A public REST API needs to be debuggable in a browser and self-documenting in Swagger. An internal service call between two Spring Boot apps needs to be fast and compact. An event streaming into Kafka needs to survive years of producer and consumer deployments that are never perfectly in sync. One serialization format optimized for all three ends up being the wrong choice for at least one of them.

I put together a small companion project — [avro-protobuf-jsonschema](https://github.com/wallaceespindola/avro-protobuf-jsonschema) — to make this comparison concrete rather than theoretical. Worth being upfront about something: the demo application in that repo is a Python/FastAPI service, not Java. I built it that way because it let me stand up all three formats — JSON Schema, Protobuf, Avro — side by side quickly, with working endpoints you can curl. But here's the thing that matters for this article: the schemas themselves (`.proto` files, `.avsc` files, JSON Schema documents) are completely language-neutral. A `.proto` file compiles to Java, Python, Go, C++, or a dozen other languages from the exact same source of truth. So everything in this article about schema design, evolution rules, and boundary selection applies whether your services are Python, Java, or both talking to each other — which, in most enterprises I've worked in, they are. The Java-specific tooling — `protoc` codegen, Avro's `SpecificRecord`, Kafka's Confluent serializers, gRPC in Spring — is where this article goes deeper than the repo's Python demo, because that's where most of you reading this actually live.

## Why Data Contracts Are Architecture, Not Plumbing

It's tempting to treat serialization format as a low-level implementation detail — something you pick once in a starter template and never revisit. In practice, the format you choose at a service boundary encodes a set of architectural decisions:

- **Who owns the schema, and how does it change over time?** JSON has no built-in answer. Protobuf and Avro both do.
- **What happens when a producer ships a new field before every consumer has upgraded?** This is schema evolution, and it's the single biggest reason teams reach for Avro or Protobuf over hand-rolled JSON.
- **How much does the wire format cost you in CPU and bandwidth?** At REST API scale this rarely matters. At Kafka-topic-with-billions-of-events scale, it's a real line item.
- **Who's consuming this data — a browser, a partner's HTTP client, or another JVM process you control end to end?** That answer changes what "developer-friendly" even means.

None of this is news to anyone who's operated a Kafka cluster or a gRPC mesh. But I still see teams default to JSON everywhere, including places where a schema registry and a binary format would have saved them a production incident. Let's look at what the alternatives actually give you, starting from the schema itself.

## Schemas as Language-Neutral Contracts

Both Protobuf and Avro start from a schema file that's independent of any programming language. That's the whole point — the schema is the contract, and code generation is just one of many things you can derive from it.

Here's the `User` message from the companion repo, exactly as it lives in [`schemas/user.proto`](https://github.com/wallaceespindola/avro-protobuf-jsonschema/blob/main/schemas/user.proto):

```proto
syntax = "proto3";

package com.example;

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;       // proto3: empty string means "default"
  bool is_active = 4;
}
```

Notice the numbered fields (`= 1`, `= 2`, and so on). Those field numbers, not the field names, are what goes on the wire. That's the mechanism behind Protobuf's schema evolution story: you can rename a field freely as long as the number stays put, and you can add new field numbers without breaking old consumers, because unrecognized numbers are just ignored. The [Protocol Buffers language guide](https://protobuf.dev/programming-guides/proto3/) covers the full set of evolution rules, including which changes are safe (adding fields, adding enum values) and which aren't (reusing a field number, changing a field's type incompatibly).

The equivalent Avro schema in the same repo, used by the `/avro/user` endpoint, looks like this:

```json
{
  "type": "record",
  "name": "User",
  "namespace": "com.example",
  "fields": [
    {"name": "id", "type": "long"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null},
    {"name": "is_active", "type": "boolean", "default": true}
  ]
}
```

Avro takes a different approach to evolution. There are no field numbers — instead, the reader and writer schemas are reconciled at deserialization time, using field names and defaults. If a writer schema has a field the reader doesn't know about, the reader drops it. If a reader schema has a field the writer didn't send, Avro falls back to the field's default value (which is why `email` and `is_active` both declare defaults above). This reader/writer reconciliation is genuinely one of Avro's strongest features, and it's described in detail in the [Avro specification](https://avro.apache.org/docs/1.12.0/specification/).

Both approaches solve the same underlying problem — decoupling the pace of producer and consumer upgrades — but they solve it differently enough that the choice matters. Protobuf's field-number scheme reads naturally to anyone used to versioned APIs. Avro's schema-reconciliation model is what makes it such a comfortable fit for a data platform, where you might be reading three-year-old Avro-encoded files with a schema that's changed a dozen times since.

## Protobuf on the JVM: Codegen, Builders, and gRPC

On the Java side, Protobuf's code generation is where the schema becomes something your IDE understands. You wire `protoc` into your Maven build with the [`protobuf-maven-plugin`](https://central.sonatype.com/artifact/org.xolstice.maven.plugins/protobuf-maven-plugin) from Xolstice, the long-standing community plugin for this job:

```xml
<build>
  <extensions>
    <extension>
      <groupId>kr.motd.maven</groupId>
      <artifactId>os-maven-plugin</artifactId>
      <version>1.7.1</version>
    </extension>
  </extensions>
  <plugins>
    <plugin>
      <groupId>org.xolstice.maven.plugins</groupId>
      <artifactId>protobuf-maven-plugin</artifactId>
      <version>0.6.1</version>
      <configuration>
        <protocArtifact>
          com.google.protobuf:protoc:3.25.5:exe:${os.detected.classifier}
        </protocArtifact>
        <protoSourceRoot>${project.basedir}/../schemas</protoSourceRoot>
      </configuration>
      <executions>
        <execution>
          <goals>
            <goal>compile</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

Point `protoSourceRoot` at the same `schemas/user.proto` file from the companion repo, and `mvn generate-sources` produces a `com.example.User` class with a builder API. One Java-specific detail: add `option java_multiple_files = true;` to the `.proto` file first, or protoc will nest the `User` message inside a generated outer wrapper class instead of emitting a top-level `com.example.User`. Using it looks like this:

```java
package com.example.demo;

import com.example.User;

public final class UserFactory {

    private UserFactory() {
    }

    public static User newActiveUser(long id, String name, String email) {
        // Generated builders are immutable once built — thread-safe to share
        return User.newBuilder()
                .setId(id)
                .setName(name)
                .setEmail(email)
                .setIsActive(true)
                .build();
    }

    public static byte[] toWireFormat(User user) {
        return user.toByteArray();
    }

    public static User fromWireFormat(byte[] bytes) throws com.google.protobuf.InvalidProtocolBufferException {
        return User.parseFrom(bytes);
    }
}
```

There's nothing exotic here on purpose. `toByteArray()` and `parseFrom()` are the two methods you'll use constantly once Protobuf is wired into a service, and they're the same shape regardless of how complex the message gets.

Where Protobuf really shows up in a Java enterprise stack is gRPC. If you're running Spring Boot, the [grpc-spring](https://github.com/grpc-ecosystem/grpc-spring) project (the actively maintained continuation of the original `grpc-spring-boot-starter`) lets you expose a gRPC service with the same `@GrpcService` annotation style you'd use for a `@RestController`:

```java
package com.example.demo.grpc;

import com.example.User;
import com.example.UserRequest;
import com.example.UserServiceGrpc;
import io.grpc.stub.StreamObserver;
import net.devh.boot.grpc.server.service.GrpcService;

@GrpcService
public class UserGrpcService extends UserServiceGrpc.UserServiceImplBase {

    @Override
    public void getUser(UserRequest request, StreamObserver<User> responseObserver) {
        User user = User.newBuilder()
                .setId(request.getId())
                .setName("Wallace")
                .setEmail("wallace@example.com")
                .setIsActive(true)
                .build();

        responseObserver.onNext(user);
        responseObserver.onCompleted();
    }
}
```

That `UserServiceGrpc.UserServiceImplBase` class is generated straight from a `.proto` service definition, the same way the `User` message class is generated from the message definition. The maven coordinates for the starter are `net.devh:grpc-server-spring-boot-starter`, documented in the [grpc-spring getting-started guide](https://grpc-ecosystem.github.io/grpc-spring/en/). This is the combination — Protobuf plus gRPC plus Spring — that most internal Java-to-Java service calls in a microservices architecture end up using, precisely because the binary wire format and HTTP/2 multiplexing together cut both payload size and connection overhead compared to REST-over-JSON for high-volume internal traffic.

## Avro on the JVM: SpecificRecord, GenericRecord, and Kafka

Avro's Java story splits into two APIs, and picking the right one matters more than it looks.

**`SpecificRecord`** generates a concrete Java class per schema, the same way Protobuf does. You wire the [`avro-maven-plugin`](https://central.sonatype.com/artifact/org.apache.avro/avro-maven-plugin) into your build, point it at a directory of `.avsc` files (the same schema shown above works unchanged), and it produces a typed `User` class with getters and a builder:

```xml
<plugin>
  <groupId>org.apache.avro</groupId>
  <artifactId>avro-maven-plugin</artifactId>
  <version>1.12.0</version>
  <executions>
    <execution>
      <phase>generate-sources</phase>
      <goals>
        <goal>schema</goal>
      </goals>
      <configuration>
        <sourceDirectory>${project.basedir}/src/main/avro</sourceDirectory>
        <outputDirectory>${project.build.directory}/generated-sources/avro</outputDirectory>
      </configuration>
    </execution>
  </executions>
</plugin>
```

```java
import com.example.User;

User user = User.newBuilder()
        .setId(1L)
        .setName("Wallace")
        .setEmail("wallace@example.com")
        .setIsActive(true)
        .build();
```

That's the version you want when you control both the producer and the schema, and you'd rather catch a typo in `setName` at compile time than at runtime.

**`GenericRecord`** skips code generation entirely and works off the parsed schema at runtime:

```java
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;

import java.io.File;

Schema schema = new Schema.Parser().parse(new File("user.avsc"));

GenericRecord user = new GenericData.Record(schema);
user.put("id", 1L);
user.put("name", "Wallace");
user.put("email", "wallace@example.com");
user.put("is_active", true);
```

This is what you reach for in generic tooling — a Kafka Streams job that processes dozens of different topic schemas, or a schema-registry-aware consumer that needs to handle types it's never seen at compile time. You give up compile-time safety, but you gain the ability to write one piece of code that works across any Avro schema.

Avro's real home, though, is Kafka. Pairing Avro with a schema registry is what makes Avro's evolution model actually enforceable across a fleet of producers and consumers you don't fully control. Here's a standard Kafka producer wired for Avro with [Confluent's Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html):

```java
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import io.confluent.kafka.serializers.KafkaAvroSerializerConfig;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.LongSerializer;

import java.util.Properties;

public final class UserEventProducer {

    private final KafkaProducer<Long, User> producer;

    public UserEventProducer(String bootstrapServers, String schemaRegistryUrl) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, LongSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);
        props.put(KafkaAvroSerializerConfig.SCHEMA_REGISTRY_URL_CONFIG, schemaRegistryUrl);
        this.producer = new KafkaProducer<>(props);
    }

    public void publish(String topic, User user) {
        producer.send(new ProducerRecord<>(topic, user.getId(), user));
        // Compatibility is enforced here, not in application code:
        // the registry rejects the write if the schema breaks the
        // configured compatibility mode (BACKWARD, FORWARD, FULL).
    }
}
```

That last comment is the important part. The schema registry isn't just a place to store `.avsc` files — it's an enforcement point. When you configure a subject's compatibility mode to `BACKWARD`, the registry physically rejects a producer trying to register a schema that would break existing consumers, before a single bad message hits the topic. That's a very different safety net than JSON, where an incompatible field change just quietly shows up in a downstream consumer's logs a week later. Confluent's [schema evolution and compatibility documentation](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) walks through each compatibility mode and what it permits.

## JSON Schema and Jackson at the REST Boundary

None of this means JSON is obsolete — it means JSON's job should be scoped to where its strengths matter: public and partner-facing REST APIs, anything a browser touches directly, and anywhere a human needs to read a payload without tooling. The companion repo's `/json/user` endpoint uses Pydantic on the Python side to generate JSON Schema automatically for OpenAPI; on the Java side, the equivalent pattern is a Spring `@RestController` backed by a Java record and validated with Bean Validation, with the JSON Schema itself generated for OpenAPI documentation via springdoc.

If you need to validate an inbound JSON payload against an externally defined JSON Schema document — say, a partner sends you a schema you don't control — the [networknt/json-schema-validator](https://github.com/networknt/json-schema-validator) library is the standard choice on the JVM:

```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;

import java.util.Set;

public final class UserPayloadValidator {

    private final JsonSchema schema;
    private final ObjectMapper mapper = new ObjectMapper();

    public UserPayloadValidator(String schemaJson) throws Exception {
        JsonSchemaFactory factory =
                JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);
        this.schema = factory.getSchema(schemaJson);
    }

    public Set<ValidationMessage> validate(String payloadJson) throws Exception {
        JsonNode payload = mapper.readTree(payloadJson);
        return schema.validate(payload);
    }
}
```

This is the same `Draft202012Validator` behavior shown in the repo's Python example, just on the JVM. It's the right tool when the schema itself is the contract with an external party and you can't assume a shared Java or Python type — the JSON document and its schema are the lowest common denominator both sides can agree on.

## The Boundary-Driven Architecture Pattern

Put these three together and you get a pattern that shows up in most mature Java platforms I've worked on, and it's the same one documented in the companion repo's README:

```
Frontend / Public APIs        →  JSON + JSON Schema (via OpenAPI)
        ↓
API Gateway / BFF
        ↓
Internal Services             →  Protobuf + gRPC
        ↓
Event Streaming / Data Platform →  Avro + Kafka + Schema Registry
```

This isn't format sprawl for its own sake — each layer picks the format that matches what's actually moving across it. A public API needs to be curl-able and self-documenting, so JSON with a well-defined JSON Schema (surfaced through OpenAPI) is the right fit. The service mesh behind the gateway is JVM process talking to JVM process (or Python to Java, in a polyglot shop), where nobody needs to eyeball the payload, and Protobuf's compactness plus gRPC's HTTP/2 transport pay for themselves at volume. And once data lands in a Kafka topic destined for long-term storage or stream processing, Avro's evolution guarantees matter more than raw throughput, because that data will outlive several generations of the schema.

## Production Considerations and Gotchas

A few things I'd flag before you adopt any of this in production:

- **Field presence in proto3 is subtle.** A `string` field with an empty value and an unset `string` field serialize identically in proto3 unless you explicitly mark it `optional`. If your Java code needs to distinguish "the client sent an empty name" from "the client didn't send a name at all," use `optional string name = 2;` in the schema — don't assume presence tracking you didn't ask for.
- **Schema registry becomes a single point of coordination, not just storage.** Treat compatibility mode changes on a registry subject with the same care as a database migration — get a second reviewer, and know your rollback path.
- **`GenericRecord` trades compile-time safety for flexibility.** Don't default to it for a well-known, stable schema just because it's more "dynamic." Use `SpecificRecord` when you own both ends of the contract.
- **gRPC isn't a drop-in replacement for REST.** Browsers can't call gRPC services directly without a proxy layer like grpc-web, and your API gateway needs to understand HTTP/2 trailers. Plan your public-facing boundary around JSON regardless of what your internal mesh uses.
- **Binary formats are opaque to your existing tooling.** A Protobuf or Avro payload dropped into a log aggregator or curl output is unreadable without the schema and the right library. Build in a debugging path — a small CLI decoder, or a dev-only JSON-echo endpoint — before you need it during an incident.

None of these are reasons to avoid Avro or Protobuf. They're reasons to be deliberate about where you introduce them and to document the trade-off for the next engineer who inherits the service.

## Summary

- JSON, Protobuf and Avro solve different problems, and the strongest architectures use each one at the boundary where its strengths matter — public APIs, internal services, and event streams respectively.
- Schemas (`.proto`, `.avsc`) are language-neutral contracts first and code-generation inputs second; the same schema drives Java, Python, or any other language your organization runs.
- On the JVM, `protoc` and the `avro-maven-plugin` both turn schemas into typed classes with builder APIs, so the ergonomics for developers end up remarkably similar despite the different wire formats underneath.
- Kafka plus Avro plus Confluent Schema Registry is the canonical Java data-pipeline pairing because the registry enforces compatibility at write time, not after a bad message has already shipped.
- gRPC plus Protobuf plus Spring gives you a fast, strongly-typed internal service mesh, but it's not a substitute for JSON at your public API boundary.

The full working code — schemas, standalone serialization examples, and a runnable FastAPI demo covering all three formats side by side — lives in the [avro-protobuf-jsonschema repository](https://github.com/wallaceespindola/avro-protobuf-jsonschema). Clone it, run the endpoints, and compare the payload sizes yourself.

## References

- Protocol Buffers Language Guide (proto3) — [protobuf.dev](https://protobuf.dev/programming-guides/proto3/)
- Apache Avro 1.12.0 Specification — [avro.apache.org](https://avro.apache.org/docs/1.12.0/specification/)
- Confluent Schema Registry: Schema Evolution and Compatibility — [docs.confluent.io](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- protobuf-maven-plugin (Xolstice) — [Maven Central](https://central.sonatype.com/artifact/org.xolstice.maven.plugins/protobuf-maven-plugin)
- avro-maven-plugin — [Maven Central](https://central.sonatype.com/artifact/org.apache.avro/avro-maven-plugin)
- grpc-spring: Spring Boot starter for gRPC — [GitHub](https://github.com/grpc-ecosystem/grpc-spring)
- networknt/json-schema-validator — [GitHub](https://github.com/networknt/json-schema-validator)
- gRPC Java documentation — [grpc.io](https://grpc.io/docs/languages/java/)

---

## Author Bio

Wallace Espindola is a senior software engineer and solution architect with hands-on experience across Java/Spring Boot, Python/FastAPI, and cloud-native microservices architecture. He builds and documents production systems that span REST, gRPC and event-streaming boundaries, and writes about the architectural trade-offs behind them.

Reach him on [LinkedIn](https://www.linkedin.com/in/wallaceespindola/) or check out his projects on [GitHub](https://github.com/wallaceespindola/).

---

Need more tech insights?
Check out my GitHub, LinkedIn, and Speaker Deck.
Happy coding!
