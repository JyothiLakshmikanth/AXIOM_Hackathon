// ===========================================================================
// AXIOM KNOWLEDGE GRAPH: E-Key 2W Digital Key Platform
// Includes full test case details & requirement traceability
// Generated from requirements_master_v5.csv & test_cases_master_v5.csv
// ===========================================================================

// --- 1. Indexes & Uniqueness Constraints ---
CREATE CONSTRAINT requirement_id_unique IF NOT EXISTS FOR (r:Requirement) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT test_case_id_unique IF NOT EXISTS FOR (t:TestCase) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT component_name_unique IF NOT EXISTS FOR (c:BusinessComponent) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT variant_id_unique IF NOT EXISTS FOR (v:Variant) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT oem_name_unique IF NOT EXISTS FOR (o:OEM) REQUIRE o.name IS UNIQUE;
CREATE CONSTRAINT artifact_type_unique IF NOT EXISTS FOR (a:ArtifactType) REQUIRE a.name IS UNIQUE;
CREATE CONSTRAINT verification_level_unique IF NOT EXISTS FOR (vl:VerificationLevel) REQUIRE vl.name IS UNIQUE;
CREATE CONSTRAINT test_suite_id_unique IF NOT EXISTS FOR (ts:TestSuite) REQUIRE ts.id IS UNIQUE;
CREATE CONSTRAINT test_plan_id_unique IF NOT EXISTS FOR (tp:TestPlan) REQUIRE tp.id IS UNIQUE;

// --- 1.1 Vector Index for Semantic & Defect Embeddings ---
CREATE VECTOR INDEX requirement_embeddings IF NOT EXISTS
FOR (r:Requirement) ON (r.embedding)
OPTIONS { indexConfig: { `vector.dimensions`: 768, `vector.similarity_function`: 'cosine' } };

// --- 2. Seed Column Value Nodes ---
MERGE (:ArtifactType {name: "Detailed System Requirement"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Data)"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Observability)"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Performance)"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Reliability)"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Scalability)"});
MERGE (:ArtifactType {name: "Detailed System Requirement (Security)"});
MERGE (:ArtifactType {name: "Non-Functional Requirement (Security)"});
MERGE (:ArtifactType {name: "Software Requirement"});
MERGE (:ArtifactType {name: "Stakeholder Requirement"});
MERGE (:ArtifactType {name: "System Requirement"});
MERGE (:VerificationLevel {name: "Acceptance"});
MERGE (:VerificationLevel {name: "Integration"});
MERGE (:VerificationLevel {name: "System"});
MERGE (:BusinessComponent {name: "Cloud Key Service"});
MERGE (:BusinessComponent {name: "Mobile App"});
MERGE (:BusinessComponent {name: "Security Module"});
MERGE (:BusinessComponent {name: "System"});
MERGE (:BusinessComponent {name: "Vehicle Controller"});
MERGE (:Variant {id: "VAR-BASE"});
MERGE (:Variant {id: "VAR-FLEET"});
MERGE (:Variant {id: "VAR-GLOB"});
MERGE (:Variant {id: "VAR-PREM"});
MERGE (:OEM {name: "All Global OEMs"});
MERGE (:OEM {name: "All OEMs"});
MERGE (:OEM {name: "OEM-A"});
MERGE (:OEM {name: "OEM-B"});
MERGE (:OEM {name: "OEM-C"});
MERGE (:OEM {name: "OEM-US"});
MERGE (:TestSuite {id: "TS-FEAT-01"});
MERGE (:TestSuite {id: "TS-FEAT-02"});
MERGE (:TestSuite {id: "TS-FEAT-03"});
MERGE (:TestSuite {id: "TS-FEAT-04"});
MERGE (:TestSuite {id: "TS-FEAT-05"});
MERGE (:TestSuite {id: "TS-FEAT-06"});
MERGE (:TestSuite {id: "TS-FEAT-07"});
MERGE (:TestSuite {id: "TS-FEAT-08"});
MERGE (:TestSuite {id: "TS-FEAT-09"});
MERGE (:TestSuite {id: "TS-FEAT-10"});
MERGE (:TestSuite {id: "TS-GLOB-COMP"});
MERGE (:TestSuite {id: "TS-GLOB-LOC"});
MERGE (:TestSuite {id: "TS-PLAT-DATA"});
MERGE (:TestSuite {id: "TS-PLAT-OBS"});
MERGE (:TestSuite {id: "TS-PLAT-PERF"});
MERGE (:TestSuite {id: "TS-PLAT-REL"});
MERGE (:TestSuite {id: "TS-PLAT-SEC"});
MERGE (:TestSuite {id: "TS-PLAT-UX"});
MERGE (:TestPlan {id: "STP-001"});
MERGE (:TestPlan {id: "STP-GLOB"});
MERGE (:TestPlan {id: "STP-PLAT"});

// --- 3. Seed Requirement Nodes with Rich Text Metadata ---
MERGE (r:Requirement {id: "REQ-L2-001"}) ON CREATE SET r.primary_text = "The vehicle owner shall be able to securely pair their smartphone with the electric two-wheeler to enable digital key functionality.", r.verification_criteria = "Demonstration: Show successful pairing process.", r.variant_implementation_notes = "Core feature across all variants.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-001"}) ON CREATE SET r.primary_text = "The E-Key 2W system shall support the secure provisioning of a digital key from the mobile application to the vehicle-side controller via the cloud lifecycle service.", r.verification_criteria = "Test: Verify end-to-end key provisioning flow.", r.variant_implementation_notes = "Standard cloud lifecycle.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-001"}) ON CREATE SET r.primary_text = "The digital key enrollment process shall complete within 15 seconds under nominal network conditions.", r.verification_criteria = "Test: Measure end-to-end enrollment time over 20 runs.", r.variant_implementation_notes = "Standard latency bound.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-001"}) ON CREATE SET r.primary_text = "The Base mobile app shall discover an eligible vehicle via standard BLE and initiate enrollment.", r.verification_criteria = "Test: Verify BLE discovery and enrollment initiation.", r.variant_implementation_notes = "BLE only discovery.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-002"}) ON CREATE SET r.primary_text = "The Premium mobile app shall require on-device biometric authentication before initiating enrollment.", r.verification_criteria = "Test: Verify biometric prompt blocks enrollment if failed.", r.variant_implementation_notes = "FaceID/TouchID integration.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-003"}) ON CREATE SET r.primary_text = "The Fleet cloud service shall support bulk CSV upload for provisioning up to 10,000 keys simultaneously.", r.verification_criteria = "Test: Upload 10k CSV and verify provisioning success rate.", r.variant_implementation_notes = "Batch processing pipeline.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-004"}) ON CREATE SET r.primary_text = "The system shall require authenticated owner identity before provisioning a digital key.", r.verification_criteria = "Test: Verify unauthenticated user cannot provision key.", r.variant_implementation_notes = "OAuth2/JWT enforcement.", r.status = "Accepted", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-002"}) ON CREATE SET r.primary_text = "The rider shall experience seamless, hands-free unlocking and locking of the vehicle based on their physical proximity.", r.verification_criteria = "Demonstration: Show vehicle unlocking as phone approaches.", r.variant_implementation_notes = "Core feature, implementation varies.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-002"}) ON CREATE SET r.primary_text = "The system shall automatically unlock or lock the vehicle when an authorized smartphone enters or leaves the defined proximity zone.", r.verification_criteria = "Test: Verify proximity-based unlock and lock actions.", r.variant_implementation_notes = "Proximity policy engine.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-002"}) ON CREATE SET r.primary_text = "The Base variant end-to-end unlock decision shall complete within 1.5 seconds under nominal conditions.", r.verification_criteria = "Test: Measure BLE unlock latency over 50 runs.", r.variant_implementation_notes = "BLE RSSI processing time.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L4-002"}) ON CREATE SET r.primary_text = "The Premium variant UWB secure ranging handshake shall complete within 800ms.", r.verification_criteria = "Test: Measure UWB handshake latency over 50 runs.", r.variant_implementation_notes = "UWB IEEE 802.15.4z latency.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-003"}) ON CREATE SET r.primary_text = "The Base vehicle controller shall unlock using standard BLE RSSI thresholds (-65 dBm).", r.verification_criteria = "Test: Verify BLE RSSI triggers unlock.", r.variant_implementation_notes = "BLE only.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-004"}) ON CREATE SET r.primary_text = "The Premium vehicle controller shall unlock using UWB precise ranging to prevent relay attacks.", r.verification_criteria = "Test: Verify UWB triggers unlock and rejects relay attacks.", r.variant_implementation_notes = "UWB secure ranging.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-005"}) ON CREATE SET r.primary_text = "The Fleet vehicle controller shall accept remote unlock commands from the Fleet Dispatcher API.", r.verification_criteria = "Test: Verify Fleet API remote unlock command actuates mechanism.", r.variant_implementation_notes = "MQTT remote command.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-006"}) ON CREATE SET r.primary_text = "The vehicle controller shall immediately reject unlock requests from an unrecognized digital key identifier.", r.verification_criteria = "Test: Unknown phone attempts to unlock; verify rejection.", r.variant_implementation_notes = "Crypto ID validation.", r.status = "Accepted", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-003"}) ON CREATE SET r.primary_text = "The system shall ensure that only authorized riders with valid permissions can start and ride the vehicle.", r.verification_criteria = "Analysis: Review security architecture.", r.variant_implementation_notes = "Core security feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-003"}) ON CREATE SET r.primary_text = "The system shall permit ride authorization only when the presented digital key is cryptographically valid, active, and not revoked.", r.verification_criteria = "Test: Verify valid key permits ride, revoked key is rejected.", r.variant_implementation_notes = "Real-time validation.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-003"}) ON CREATE SET r.primary_text = "The vehicle ignition enable signal shall be triggered within 500ms of the mobile app sending the 'Ready to Ride' command.", r.verification_criteria = "Test: Measure time between app command and ignition relay.", r.variant_implementation_notes = "Ignition relay latency.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-007"}) ON CREATE SET r.primary_text = "The mobile application shall provide a clear UI indicator showing whether ride authorization is currently active.", r.verification_criteria = "Test: Verify rider can view active ride authorization status.", r.variant_implementation_notes = "UI state management.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-008"}) ON CREATE SET r.primary_text = "The vehicle controller shall execute a cryptographic challenge-response handshake before enabling ignition.", r.verification_criteria = "Test: Verify ignition is disabled if crypto handshake fails.", r.variant_implementation_notes = "AES-256 challenge-response.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-004"}) ON CREATE SET r.primary_text = "The vehicle owner shall be able to share constrained, temporary digital key access with other riders securely.", r.verification_criteria = "Demonstration: Show owner creating a shared key.", r.variant_implementation_notes = "Core sharing feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-004"}) ON CREATE SET r.primary_text = "The cloud key lifecycle service shall allow an owner to generate and distribute a shared digital key with configurable constraints.", r.verification_criteria = "Test: Verify shared key expires and respects permissions.", r.variant_implementation_notes = "Constraint engine.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-009"}) ON CREATE SET r.primary_text = "The Base cloud service shall enforce time-based expiry constraints on shared keys.", r.verification_criteria = "Test: Verify shared key expires at configured time.", r.variant_implementation_notes = "Time-based ACL.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-010"}) ON CREATE SET r.primary_text = "The Premium cloud service shall enforce geofencing constraints on shared keys.", r.verification_criteria = "Test: Verify shared key fails if used outside defined geo-zone.", r.variant_implementation_notes = "Geo-fencing ACL.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-011"}) ON CREATE SET r.primary_text = "The mobile application shall display a list of all currently active shared keys and their constraints.", r.verification_criteria = "Test: Verify owner sees active shared keys list.", r.variant_implementation_notes = "List UI component.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-005"}) ON CREATE SET r.primary_text = "The vehicle owner shall have the ability to instantly revoke digital key access in case of loss or theft.", r.verification_criteria = "Demonstration: Show owner revoking a key.", r.variant_implementation_notes = "Critical security feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-005"}) ON CREATE SET r.primary_text = "The system shall support immediate revocation of a shared digital key, propagating status to vehicle and mobile.", r.verification_criteria = "Test: Verify owner can revoke and measure propagation time.", r.variant_implementation_notes = "CRL propagation.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-005"}) ON CREATE SET r.primary_text = "A revocation command received by the vehicle online shall become effective within 10 seconds.", r.verification_criteria = "Test: Measure online revocation propagation time.", r.variant_implementation_notes = "Propagation latency.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-012"}) ON CREATE SET r.primary_text = "The Fleet cloud service shall support bulk API revocation for up to 1,000 keys simultaneously.", r.verification_criteria = "Test: Verify bulk API revokes 1k keys within 30s.", r.variant_implementation_notes = "Bulk batch processing.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-006"}) ON CREATE SET r.primary_text = "The system shall allow owners to customize rider access based on specific time windows or usage restrictions.", r.verification_criteria = "Analysis: Review UI/UX and permission schemas.", r.variant_implementation_notes = "Premium/Fleet only feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-006"}) ON CREATE SET r.primary_text = "The system shall support the configuration and enforcement of rider profiles, including time-window access.", r.verification_criteria = "Test: Verify rider access is denied outside time window.", r.variant_implementation_notes = "Policy engine.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-013"}) ON CREATE SET r.primary_text = "The Premium mobile app shall allow the owner to restrict a specific rider's access to a configured time window.", r.verification_criteria = "Test: Verify owner can set and save time window.", r.variant_implementation_notes = "Time-picker UI.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-014"}) ON CREATE SET r.primary_text = "The Fleet Dashboard shall allow admins to assign shift-based profiles to riders.", r.verification_criteria = "Test: Verify rider can only unlock during assigned shift.", r.variant_implementation_notes = "Shift management integration.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-007"}) ON CREATE SET r.primary_text = "The system shall provide a secure, temporary access mode for valet or service personnel.", r.verification_criteria = "Demonstration: Show creation and usage of a temporary service key.", r.variant_implementation_notes = "Core feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-007"}) ON CREATE SET r.primary_text = "The system shall allow the generation of a temporary service key with predefined, limited permissions.", r.verification_criteria = "Test: Verify temporary service key works only with restricted permissions.", r.variant_implementation_notes = "Permission masking.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-015"}) ON CREATE SET r.primary_text = "The Base vehicle controller shall limit max speed to 20km/h when a service key is active.", r.verification_criteria = "Test: Verify speed is limited under valet mode.", r.variant_implementation_notes = "Speed limiter logic.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-016"}) ON CREATE SET r.primary_text = "The Premium vehicle controller shall disable trunk release and limit speed when a service key is active.", r.verification_criteria = "Test: Verify trunk disabled and speed limited.", r.variant_implementation_notes = "Advanced permission masking.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-008"}) ON CREATE SET r.primary_text = "The system shall maintain a secure, auditable log of all security-relevant events.", r.verification_criteria = "Inspection: Review security event log schema.", r.variant_implementation_notes = "Compliance feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-008"}) ON CREATE SET r.primary_text = "The system shall record all failed authorization attempts and expose them only to authorized users.", r.verification_criteria = "Test: Verify failed attempts create event and unauthorized users cannot read.", r.variant_implementation_notes = "Audit logging.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-006"}) ON CREATE SET r.primary_text = "The Base variant shall retain security logs for a minimum of 1 year.", r.verification_criteria = "Inspection: Verify cloud DB retention policy.", r.variant_implementation_notes = "Cost-optimized retention.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L4-007"}) ON CREATE SET r.primary_text = "The Premium variant shall retain high-fidelity telemetry and security logs for 5 years immutably.", r.verification_criteria = "Inspection: Verify Data Lake retention and WORM policy.", r.variant_implementation_notes = "Premium compliance tier.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-017"}) ON CREATE SET r.primary_text = "The Fleet variant shall stream security events to external SIEM systems via Webhook.", r.verification_criteria = "Test: Verify SIEM receives formatted security events.", r.variant_implementation_notes = "SIEM integration.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-009"}) ON CREATE SET r.primary_text = "The user shall be able to remotely check the basic status of the vehicle.", r.verification_criteria = "Demonstration: Show app displaying accurate status.", r.variant_implementation_notes = "Core feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-009"}) ON CREATE SET r.primary_text = "The system shall periodically synchronize and display the vehicle's latest known connection status and battery.", r.verification_criteria = "Test: Verify app shows latest lock state and battery.", r.variant_implementation_notes = "Telemetry sync.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-018"}) ON CREATE SET r.primary_text = "The Base app shall display lock state via standard REST polling every 60s.", r.verification_criteria = "Test: Verify app UI reflects lock state.", r.variant_implementation_notes = "REST polling.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-019"}) ON CREATE SET r.primary_text = "The Premium app shall receive real-time lock state updates via WebSockets.", r.verification_criteria = "Test: Verify app updates instantly on lock change.", r.variant_implementation_notes = "WebSocket push.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-020"}) ON CREATE SET r.primary_text = "The Fleet Dashboard shall display real-time telemetry for 10k vehicles via WebSockets.", r.verification_criteria = "Test: Verify dashboard updates 10k pins within 5s.", r.variant_implementation_notes = "High-scale WebSockets.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L2-010"}) ON CREATE SET r.primary_text = "The vehicle shall remain operable for a limited period if cloud connectivity is temporarily lost.", r.verification_criteria = "Analysis: Review offline grace period risk assessment.", r.variant_implementation_notes = "Resilience feature.", r.status = "Accepted", r.level = "L2";
MERGE (r:Requirement {id: "REQ-L3-010"}) ON CREATE SET r.primary_text = "The system shall support a limited offline grace period, allowing ride authorization without real-time cloud validation.", r.verification_criteria = "Test: Verify vehicle permits offline grace and rejects after expiry.", r.variant_implementation_notes = "Offline cache logic.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L4-009"}) ON CREATE SET r.primary_text = "The maximum allowable offline grace period shall be 72 hours.", r.verification_criteria = "Test: Simulate 73 hours offline; verify vehicle rejects ride.", r.variant_implementation_notes = "Security bound.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-021"}) ON CREATE SET r.primary_text = "The offline grace mode shall strictly terminate when its configured validity window expires.", r.verification_criteria = "Test: Verify expired offline grace is rejected.", r.variant_implementation_notes = "Hard timeout logic.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L3-037"}) ON CREATE SET r.primary_text = "The platform shall enforce TLS 1.3 encryption for all data in transit.", r.verification_criteria = "Inspection: Review network captures for TLS 1.3.", r.variant_implementation_notes = "Platform baseline.", r.status = "Accepted", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L3-038"}) ON CREATE SET r.primary_text = "The platform shall enforce AES-256 encryption for all sensitive data at rest in databases and object storage.", r.verification_criteria = "Inspection: Verify database and S3/GCS bucket encryption settings.", r.variant_implementation_notes = "SOC2/ISO27001 baseline.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-037"}) ON CREATE SET r.primary_text = "The platform shall manage all API keys, database credentials, and cryptographic seeds via a centralized secrets manager.", r.verification_criteria = "Test: Verify no hardcoded secrets exist in source code or environment variables.", r.variant_implementation_notes = "Zero-trust architecture.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L4-037"}) ON CREATE SET r.primary_text = "The platform shall undergo automated container vulnerability scanning in the CI/CD pipeline before deployment.", r.verification_criteria = "Test: Introduce a CVE into a Dockerfile; verify pipeline blocks deployment.", r.variant_implementation_notes = "Shift-left security.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L3-039"}) ON CREATE SET r.primary_text = "The Global variant shall enforce data residency (EU in Frankfurt, US in Oregon).", r.verification_criteria = "Inspection: Verify cloud DB region routing.", r.variant_implementation_notes = "GDPR/CCPA compliance.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L3-040"}) ON CREATE SET r.primary_text = "The Global variant shall comply with CCPA by providing an 'Opt-Out of Sale of Personal Information' mechanism.", r.verification_criteria = "Test: Verify user can toggle opt-out and data sharing ceases.", r.variant_implementation_notes = "California privacy law.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-038"}) ON CREATE SET r.primary_text = "The system shall provide a 'Right to be Forgotten' API endpoint that permanently deletes all user PII within 30 days.", r.verification_criteria = "Test: Call deletion API; verify DB records are purged.", r.variant_implementation_notes = "GDPR Art. 17.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-039"}) ON CREATE SET r.primary_text = "The mobile app shall implement a granular consent management UI for data collection (analytics, location, push notifications).", r.verification_criteria = "Test: Verify app respects user consent toggles in real-time.", r.variant_implementation_notes = "ePrivacy Directive.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-040"}) ON CREATE SET r.primary_text = "The system shall provide a 'Data Portability' API endpoint allowing users to export all their data in a machine-readable JSON format.", r.verification_criteria = "Test: Call export API; verify JSON contains all user PII and activity logs.", r.variant_implementation_notes = "GDPR Art. 20.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L4-038"}) ON CREATE SET r.primary_text = "The API Gateway shall enforce rate limiting of 100 requests/minute per user to prevent abuse and DDoS.", r.verification_criteria = "Test: Send 101 requests in 60s; verify 429 Too Many Requests response.", r.variant_implementation_notes = "Standard API protection.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L4-039"}) ON CREATE SET r.primary_text = "The platform shall utilize read replicas for the primary database to offload read-heavy telemetry queries.", r.verification_criteria = "Analysis: Review database architecture diagram for read replica configuration.", r.variant_implementation_notes = "Database scaling strategy.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-041"}) ON CREATE SET r.primary_text = "The platform shall serve all static mobile app assets (images, binaries) via a global Content Delivery Network (CDN).", r.verification_criteria = "Test: Request asset from US and EU; verify response from nearest edge location.", r.variant_implementation_notes = "Latency reduction.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L4-040"}) ON CREATE SET r.primary_text = "Core platform services (Auth, Key Lifecycle) shall be deployed across multiple Availability Zones (Multi-AZ).", r.verification_criteria = "Inspection: Review cloud infrastructure deployment topology.", r.variant_implementation_notes = "High availability baseline.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L4-041"}) ON CREATE SET r.primary_text = "The platform shall perform automated daily backups of all databases with a Point-in-Time Recovery (PITR) window of 35 days.", r.verification_criteria = "Test: Simulate data corruption; restore database to 1 hour prior.", r.variant_implementation_notes = "Disaster recovery.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L3-041"}) ON CREATE SET r.primary_text = "The platform shall implement graceful degradation; if the Cloud Key Service is unreachable, the Mobile App shall cache the last known state and queue actions.", r.verification_criteria = "Test: Block cloud access; verify app queues actions and syncs when restored.", r.variant_implementation_notes = "Offline-first UX.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-042"}) ON CREATE SET r.primary_text = "The platform shall aggregate all application, security, and access logs into a centralized logging service.", r.verification_criteria = "Test: Generate log in microservice A; verify it appears in centralized dashboard.", r.variant_implementation_notes = "Centralized observability.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L4-042"}) ON CREATE SET r.primary_text = "The platform shall trigger automated alerts (PagerDuty/Slack) when API error rates exceed 1% over a 5-minute window.", r.verification_criteria = "Test: Inject 500 errors; verify alert is triggered within 5 minutes.", r.variant_implementation_notes = "Proactive incident response.", r.status = "Draft", r.level = "L4";
MERGE (r:Requirement {id: "REQ-L5-043"}) ON CREATE SET r.primary_text = "The platform shall implement distributed tracing (OpenTelemetry) to track request flows across Mobile, API Gateway, and Microservices.", r.verification_criteria = "Test: Generate request; verify trace ID is present in all downstream service logs.", r.variant_implementation_notes = "Root cause analysis.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-044"}) ON CREATE SET r.primary_text = "The platform shall implement automated data lifecycle policies, moving telemetry older than 90 days to cold storage.", r.verification_criteria = "Test: Insert record with timestamp > 90 days; verify it moves to cold storage.", r.variant_implementation_notes = "Cost optimization.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L3-042"}) ON CREATE SET r.primary_text = "The Global variant shall handle all time-based operations (rider profiles, logs) in UTC and convert to local timezone at the presentation layer.", r.verification_criteria = "Test: Create time-window in Tokyo; verify it displays correctly in New York.", r.variant_implementation_notes = "Timezone agnostic backend.", r.status = "Draft", r.level = "L3";
MERGE (r:Requirement {id: "REQ-L5-045"}) ON CREATE SET r.primary_text = "The platform shall enforce ISO 8601 standards for all date and time data exchanged via APIs.", r.verification_criteria = "Test: Verify all API JSON responses use 'YYYY-MM-DDTHH:mm:ssZ' format.", r.variant_implementation_notes = "Standardized data exchange.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L5-046"}) ON CREATE SET r.primary_text = "The mobile app shall support dynamic localization for 15 languages based on device OS settings.", r.verification_criteria = "Test: Change device language to Japanese; verify app UI updates.", r.variant_implementation_notes = "i18n resource bundles.", r.status = "Draft", r.level = "L5";
MERGE (r:Requirement {id: "REQ-L3-043"}) ON CREATE SET r.primary_text = "The mobile application and web dashboards shall comply with WCAG 2.1 Level AA accessibility standards.", r.verification_criteria = "Test: Run automated accessibility scanner (e.g., axe-core); verify zero critical violations.", r.variant_implementation_notes = "Inclusive design.", r.status = "Draft", r.level = "L3";

// --- 4. Seed TestCase Nodes with Full Details from test_cases_master_v5.csv ---
MERGE (t:TestCase {id: "TC-ENR-001"}) ON CREATE SET t.description = "Validates that a Base variant vehicle can be discovered via BLE and successfully initiates the enrollment sequence.", t.objective = "Verify BLE pairing on Base.", t.preconditions = "Vehicle BLE ON.", t.steps = "1. Open App. 2. Scan.", t.expected_result = "Pairing succeeds.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-002"}) ON CREATE SET t.description = "Validates that a Premium variant vehicle utilizes UWB for secure discovery and enrollment initiation.", t.objective = "Verify UWB pairing on Premium.", t.preconditions = "Vehicle UWB ON.", t.steps = "1. Open App. 2. Scan.", t.expected_result = "UWB pairing succeeds.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-003"}) ON CREATE SET t.description = "Validates the end-to-end flow of provisioning a digital key from the mobile app through the cloud to the vehicle controller.", t.objective = "Verify end-to-end cloud provisioning.", t.preconditions = "Cloud service running.", t.steps = "1. Initiate enroll. 2. Check DB.", t.expected_result = "Key record created.", t.test_type = "Functional", t.priority = "Critical", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-004"}) ON CREATE SET t.description = "Measures the total time taken for the digital key enrollment process under nominal network conditions.", t.objective = "Measure enrollment latency.", t.preconditions = "Network stable.", t.steps = "1. Start timer. 2. Stop on success.", t.expected_result = "Time < 15s.", t.test_type = "Performance", t.priority = "High", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-005"}) ON CREATE SET t.description = "Validates that the Base mobile app correctly discovers eligible vehicles using standard BLE protocols.", t.objective = "Verify Base BLE discovery.", t.preconditions = "App installed.", t.steps = "1. Scan for BLE.", t.expected_result = "Vehicle appears.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-006"}) ON CREATE SET t.description = "Validates that the Premium app enforces on-device biometric authentication before allowing key provisioning.", t.objective = "Verify Premium biometric block.", t.preconditions = "Biometrics disabled.", t.steps = "1. Attempt enroll.", t.expected_result = "Blocked.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-007"}) ON CREATE SET t.description = "Validates the Fleet cloud service's ability to process bulk CSV uploads for mass key provisioning.", t.objective = "Verify Fleet bulk CSV upload.", t.preconditions = "10k CSV ready.", t.steps = "1. Upload CSV.", t.expected_result = "10k keys provisioned.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-B2B", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-ENR-008"}) ON CREATE SET t.description = "Validates that unauthenticated users are blocked from initiating the digital key enrollment process.", t.objective = "Verify unauthenticated user blocked.", t.preconditions = "User logged out.", t.steps = "1. Attempt enroll.", t.expected_result = "Prompt for login.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-01", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-001"}) ON CREATE SET t.description = "Validates that a Base variant vehicle automatically unlocks when an authorized phone enters the BLE proximity zone.", t.objective = "Verify Base passive unlock.", t.preconditions = "Phone BLE ON.", t.steps = "1. Approach vehicle.", t.expected_result = "Unlocks.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-002"}) ON CREATE SET t.description = "Validates that a Premium variant vehicle securely unlocks using UWB precise ranging.", t.objective = "Verify Premium UWB unlock.", t.preconditions = "Phone UWB ON.", t.steps = "1. Approach vehicle.", t.expected_result = "Unlocks securely.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-003"}) ON CREATE SET t.description = "Validates the system's proximity policy engine correctly triggers actions when crossing defined boundaries.", t.objective = "Verify proximity policy engine.", t.preconditions = "Policy configured.", t.steps = "1. Cross boundary.", t.expected_result = "Action triggers.", t.test_type = "Functional", t.priority = "Critical", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-004"}) ON CREATE SET t.description = "Measures the end-to-end unlock latency for the Base variant using BLE RSSI over 50 runs.", t.objective = "Measure Base BLE latency.", t.preconditions = "Nominal conditions.", t.steps = "1. Execute 50 times.", t.expected_result = "p95 < 1.5s.", t.test_type = "Performance", t.priority = "Critical", t.status = "Fail", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-005"}) ON CREATE SET t.description = "Measures the secure ranging handshake latency for the Premium variant using UWB over 50 runs.", t.objective = "Measure Premium UWB latency.", t.preconditions = "UWB active.", t.steps = "1. Execute 50 times.", t.expected_result = "p95 < 800ms.", t.test_type = "Performance", t.priority = "Critical", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-006"}) ON CREATE SET t.description = "Validates that the Base vehicle controller unlocks specifically when BLE RSSI crosses the -64 dBm threshold.", t.objective = "Verify Base BLE RSSI unlock.", t.preconditions = "Phone at -70 dBm.", t.steps = "1. Move to -64 dBm.", t.expected_result = "Unlocks.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-007"}) ON CREATE SET t.description = "Validates that the Premium UWB system successfully rejects a simulated BLE relay attack.", t.objective = "Verify Premium UWB relay attack prevention.", t.preconditions = "Attacker has relay.", t.steps = "1. Attempt relay.", t.expected_result = "Fails. UWB unlocks.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-008"}) ON CREATE SET t.description = "Validates that the Fleet vehicle controller accepts and executes remote unlock commands via the Fleet API.", t.objective = "Verify Fleet remote API unlock.", t.preconditions = "API creds valid.", t.steps = "1. Send remote cmd.", t.expected_result = "Unlocks remotely.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-B2B", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-UNL-009"}) ON CREATE SET t.description = "Validates that the vehicle controller immediately rejects unlock requests from unrecognized digital key identifiers.", t.objective = "Verify unknown key rejection.", t.preconditions = "Unknown phone.", t.steps = "1. Approach vehicle.", t.expected_result = "Stays locked.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-02", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-001"}) ON CREATE SET t.description = "Validates that an authorized rider with a valid key can successfully start the vehicle.", t.objective = "Verify authorized ride start.", t.preconditions = "Key valid.", t.steps = "1. Tap Start.", t.expected_result = "Ride starts.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-002"}) ON CREATE SET t.description = "Validates that the system permits ride authorization only when the cryptographic key is valid.", t.objective = "Verify valid key permits ride.", t.preconditions = "Key valid.", t.steps = "1. Tap Start.", t.expected_result = "Permitted.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-003"}) ON CREATE SET t.description = "Validates that the system rejects ride authorization attempts using a revoked digital key.", t.objective = "Verify revoked key rejected.", t.preconditions = "Key revoked.", t.steps = "1. Tap Start.", t.expected_result = "Rejected.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-004"}) ON CREATE SET t.description = "Measures the latency between the mobile app 'Start' command and the physical ignition relay closure.", t.objective = "Measure ignition latency.", t.preconditions = "Network stable.", t.steps = "1. Tap Start. 2. Measure relay.", t.expected_result = "< 500ms.", t.test_type = "Performance", t.priority = "High", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-005"}) ON CREATE SET t.description = "Validates that the mobile app UI correctly displays the active ride authorization status to the rider.", t.objective = "Verify UI shows active status.", t.preconditions = "Ride active.", t.steps = "1. Check App.", t.expected_result = "Shows 'Active'.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-RID-006"}) ON CREATE SET t.description = "Validates that the ignition remains disabled if the cryptographic challenge-response handshake fails or times out.", t.objective = "Verify crypto handshake failure blocks ignition.", t.preconditions = "Simulate timeout.", t.steps = "1. Tap Start.", t.expected_result = "Ignition disabled.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-03", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SHR-001"}) ON CREATE SET t.description = "Validates that an authenticated vehicle owner can successfully create and distribute a shared digital key.", t.objective = "Verify owner can share key.", t.preconditions = "Owner logged in.", t.steps = "1. Create shared key.", t.expected_result = "Key created.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-04", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SHR-002"}) ON CREATE SET t.description = "Validates that a shared digital key strictly enforces the constraints (e.g., permissions) assigned by the owner.", t.objective = "Verify shared key respects constraints.", t.preconditions = "Constraint set.", t.steps = "1. Use shared key.", t.expected_result = "Constraint enforced.", t.test_type = "Functional", t.priority = "Critical", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-04", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SHR-003"}) ON CREATE SET t.description = "Validates that a Base variant shared key correctly expires and fails authentication after the configured time window.", t.objective = "Verify Base time-expiry constraint.", t.preconditions = "Expiry set to 1h.", t.steps = "1. Wait 61 mins. 2. Use key.", t.expected_result = "Fails.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-04", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SHR-004"}) ON CREATE SET t.description = "Validates that a Premium variant shared key fails authentication if used outside the defined geofencing zone.", t.objective = "Verify Premium geo-fencing constraint.", t.preconditions = "Geo-zone set.", t.steps = "1. Use key outside zone.", t.expected_result = "Fails.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-04", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SHR-005"}) ON CREATE SET t.description = "Validates that the mobile app correctly renders a list of all active shared keys and their specific constraints.", t.objective = "Verify shared keys list UI.", t.preconditions = "2 keys active.", t.steps = "1. Open list.", t.expected_result = "Shows 2 keys.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-04", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-REV-001"}) ON CREATE SET t.description = "Validates that an owner can successfully revoke an active shared digital key via the mobile app.", t.objective = "Verify owner can revoke key.", t.preconditions = "Key active.", t.steps = "1. Tap Revoke.", t.expected_result = "Key revoked.", t.test_type = "Functional", t.priority = "Critical", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-05", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-REV-002"}) ON CREATE SET t.description = "Validates that a revocation command successfully propagates from the cloud to the vehicle controller.", t.objective = "Verify revocation propagates.", t.preconditions = "Vehicle online.", t.steps = "1. Revoke. 2. Check vehicle.", t.expected_result = "Vehicle rejects key.", t.test_type = "Functional", t.priority = "Critical", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-05", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-REV-003"}) ON CREATE SET t.description = "Measures the time taken for a revocation command to propagate from the cloud to the vehicle controller.", t.objective = "Measure revocation propagation.", t.preconditions = "Vehicle online.", t.steps = "1. Revoke. 2. Measure time.", t.expected_result = "< 10s.", t.test_type = "Performance", t.priority = "Critical", t.status = "Fail", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-05", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-REV-004"}) ON CREATE SET t.description = "Validates the Fleet API's ability to process bulk revocation requests for up to 1,000 keys simultaneously.", t.objective = "Verify Fleet bulk API revocation.", t.preconditions = "1k keys active.", t.steps = "1. Call bulk API.", t.expected_result = "1k keys revoked.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-B2B", t.suite_id = "TS-FEAT-05", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-PRF-001"}) ON CREATE SET t.description = "Validates that the Premium mobile app allows an owner to configure and save a specific time-window restriction.", t.objective = "Verify Premium time-window UI.", t.preconditions = "Premium app.", t.steps = "1. Set time window.", t.expected_result = "Saved.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-06", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-PRF-002"}) ON CREATE SET t.description = "Validates that the cloud policy engine correctly denies ride authorization when attempted outside a configured time window.", t.objective = "Verify policy engine denies outside window.", t.preconditions = "Outside window.", t.steps = "1. Attempt ride.", t.expected_result = "Denied.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-06", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-PRF-003"}) ON CREATE SET t.description = "Validates the functionality of the time-picker UI component within the Premium mobile application.", t.objective = "Verify Premium time-picker UI.", t.preconditions = "Premium app.", t.steps = "1. Set 09:00-17:00.", t.expected_result = "Saved.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-06", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-PRF-004"}) ON CREATE SET t.description = "Validates that the Fleet Dashboard correctly assigns shift-based profiles and restricts rider access accordingly.", t.objective = "Verify Fleet shift-profile assignment.", t.preconditions = "Fleet dashboard.", t.steps = "1. Assign shift.", t.expected_result = "Rider restricted to shift.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-B2B", t.suite_id = "TS-FEAT-06", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-VLT-001"}) ON CREATE SET t.description = "Validates that an owner can successfully generate a temporary valet or service key.", t.objective = "Verify valet key creation.", t.preconditions = "Owner logged in.", t.steps = "1. Create valet key.", t.expected_result = "Created.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-07", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-VLT-002"}) ON CREATE SET t.description = "Validates that a valet key correctly masks permissions, rejecting any owner-level actions.", t.objective = "Verify valet permissions masked.", t.preconditions = "Valet key active.", t.steps = "1. Attempt owner action.", t.expected_result = "Rejected.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-07", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-VLT-003"}) ON CREATE SET t.description = "Validates that the Base vehicle controller enforces a 20km/h speed limit when a valet key is active.", t.objective = "Verify Base valet speed limit.", t.preconditions = "Valet key active.", t.steps = "1. Accelerate.", t.expected_result = "Capped at 20km/h.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-07", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-VLT-004"}) ON CREATE SET t.description = "Validates that the Premium vehicle controller disables the trunk release mechanism when a valet key is active.", t.objective = "Verify Premium valet trunk disable.", t.preconditions = "Valet key active.", t.steps = "1. Attempt trunk release.", t.expected_result = "Disabled.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-07", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-001"}) ON CREATE SET t.description = "Validates that the system correctly logs a security event when an unknown key attempts to unlock the vehicle.", t.objective = "Verify security event logging.", t.preconditions = "Vehicle locked.", t.steps = "1. Attempt unknown unlock.", t.expected_result = "Event logged.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-002"}) ON CREATE SET t.description = "Validates that unauthorized users receive a 403 Forbidden error when attempting to access security event logs.", t.objective = "Verify unauthorized user cannot read logs.", t.preconditions = "User B requests User A logs.", t.steps = "1. Call API.", t.expected_result = "403 Forbidden.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-003"}) ON CREATE SET t.description = "Validates that multiple failed authentication attempts generate distinct, timestamped log events.", t.objective = "Verify failed auth creates event.", t.preconditions = "Unknown key.", t.steps = "1. Attempt unlock 3x.", t.expected_result = "3 events logged.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-004"}) ON CREATE SET t.description = "Validates that the Base variant cloud database enforces a 1-year retention policy for security logs.", t.objective = "Verify Base 1-year retention.", t.preconditions = "Base DB.", t.steps = "1. Check policy.", t.expected_result = "365 days.", t.test_type = "Compliance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-005"}) ON CREATE SET t.description = "Validates that the Premium variant Data Lake enforces a 5-year immutable (WORM) retention policy.", t.objective = "Verify Premium 5-year immutable retention.", t.preconditions = "Premium Data Lake.", t.steps = "1. Check policy.", t.expected_result = "1825 days, WORM.", t.test_type = "Compliance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-SEC-006"}) ON CREATE SET t.description = "Validates that the Fleet variant correctly streams security events to an external SIEM via webhook.", t.objective = "Verify Fleet SIEM webhook.", t.preconditions = "SIEM listener active.", t.steps = "1. Trigger event.", t.expected_result = "SIEM receives payload.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-B2B", t.suite_id = "TS-FEAT-08", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-STS-001"}) ON CREATE SET t.description = "Validates that the mobile app correctly displays the current lock state of the vehicle.", t.objective = "Verify status display.", t.preconditions = "Vehicle locked.", t.steps = "1. Open App.", t.expected_result = "Shows locked.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-09", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-STS-002"}) ON CREATE SET t.description = "Validates that the system successfully synchronizes telemetry data from the vehicle to the mobile app.", t.objective = "Verify telemetry sync.", t.preconditions = "Vehicle awake.", t.steps = "1. Check App.", t.expected_result = "Updates.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-09", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-STS-003"}) ON CREATE SET t.description = "Validates that the Base app updates the lock state UI via standard REST polling within 60 seconds.", t.objective = "Verify Base REST polling.", t.preconditions = "Vehicle locked.", t.steps = "1. Pull to refresh.", t.expected_result = "Updates within 60s.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-FEAT-09", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-STS-004"}) ON CREATE SET t.description = "Validates that the Premium app receives and displays real-time lock state updates via WebSockets.", t.objective = "Verify Premium WebSocket push.", t.preconditions = "WebSocket active.", t.steps = "1. Change lock state.", t.expected_result = "Updates instantly.", t.test_type = "Performance", t.priority = "High", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-09", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-STS-005"}) ON CREATE SET t.description = "Validates that the Fleet Dashboard can handle and render real-time telemetry updates for 10,000 simulated vehicles.", t.objective = "Verify Fleet 10k WebSocket scale.", t.preconditions = "10k simulated.", t.steps = "1. Change 1k states.", t.expected_result = "Updates within 5s.", t.test_type = "Performance", t.priority = "Critical", t.status = "Not Run", t.owner = "QA-PERF", t.suite_id = "TS-FEAT-09", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-OFF-001"}) ON CREATE SET t.description = "Validates that the vehicle permits ride authorization during the offline grace period.", t.objective = "Verify offline grace permits ride.", t.preconditions = "Offline 2h.", t.steps = "1. Attempt ride.", t.expected_result = "Permitted.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-10", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-OFF-002"}) ON CREATE SET t.description = "Validates that the vehicle rejects ride authorization once the offline grace period has expired.", t.objective = "Verify offline grace rejects after expiry.", t.preconditions = "Offline 73h.", t.steps = "1. Attempt ride.", t.expected_result = "Rejected.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-10", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-OFF-003"}) ON CREATE SET t.description = "Validates that the vehicle's local authorization cache survives a complete power cycle.", t.objective = "Verify local cache survives power cycle.", t.preconditions = "Power cycle.", t.steps = "1. Check cache.", t.expected_result = "Persists.", t.test_type = "Functional", t.priority = "High", t.status = "Pass", t.owner = "QA-02", t.suite_id = "TS-FEAT-10", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-OFF-004"}) ON CREATE SET t.description = "Validates the strict 72-hour hard limit for the offline grace mode.", t.objective = "Verify 72h hard limit.", t.preconditions = "Offline 73h.", t.steps = "1. Attempt ride.", t.expected_result = "Rejected.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-10", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-OFF-005"}) ON CREATE SET t.description = "Validates the hard timeout logic that strictly terminates offline grace mode.", t.objective = "Verify hard timeout logic.", t.preconditions = "Timeout reached.", t.steps = "1. Attempt ride.", t.expected_result = "Rejected.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-FEAT-10", t.plan_id = "STP-001";
MERGE (t:TestCase {id: "TC-037"}) ON CREATE SET t.description = "Validates that all API and cross-service communication strictly enforces TLS 1.3 encryption.", t.objective = "Verify TLS 1.3 enforcement.", t.preconditions = "Wireshark active.", t.steps = "1. Capture API traffic.", t.expected_result = "Handshake uses TLS 1.3.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-PLAT-SEC", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-038"}) ON CREATE SET t.description = "Validates that sensitive data stored in databases and object storage is encrypted using AES-256.", t.objective = "Verify AES-256 encryption at rest.", t.preconditions = "Database access.", t.steps = "1. Inspect DB config.", t.expected_result = "Encryption enabled.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-PLAT-SEC", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-039"}) ON CREATE SET t.description = "Validates that no hardcoded secrets exist in the source code or environment variables.", t.objective = "Verify no hardcoded secrets.", t.preconditions = "Source code access.", t.steps = "1. Run secret scanning tool.", t.expected_result = "Zero secrets found.", t.test_type = "Security", t.priority = "Critical", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-PLAT-SEC", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-040"}) ON CREATE SET t.description = "Validates that the CI/CD pipeline automatically blocks deployment if container vulnerabilities are detected.", t.objective = "Verify CI/CD vulnerability scanning.", t.preconditions = "CI/CD pipeline access.", t.steps = "1. Push code with CVE.", t.expected_result = "Pipeline fails.", t.test_type = "Security", t.priority = "High", t.status = "Pass", t.owner = "QA-SEC", t.suite_id = "TS-PLAT-SEC", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-041"}) ON CREATE SET t.description = "Validates that user data for EU residents is strictly routed and stored in the Frankfurt region.", t.objective = "Verify EU data residency.", t.preconditions = "EU IP.", t.steps = "1. Create user.", t.expected_result = "Stored in Frankfurt.", t.test_type = "Compliance", t.priority = "Critical", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-GLOB-COMP", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-042"}) ON CREATE SET t.description = "Validates that US users can successfully toggle the CCPA 'Opt-Out of Sale' mechanism.", t.objective = "Verify CCPA opt-out mechanism.", t.preconditions = "US User.", t.steps = "1. Toggle opt-out.", t.expected_result = "Data sharing stops.", t.test_type = "Compliance", t.priority = "High", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-GLOB-COMP", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-043"}) ON CREATE SET t.description = "Validates that the 'Right to be Forgotten' API permanently purges all user PII from the database.", t.objective = "Verify Right to be Forgotten.", t.preconditions = "User exists.", t.steps = "1. Call DELETE API.", t.expected_result = "PII purged.", t.test_type = "Compliance", t.priority = "High", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-GLOB-COMP", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-044"}) ON CREATE SET t.description = "Validates that the mobile app correctly respects user consent toggles for data collection in real-time.", t.objective = "Verify granular consent UI.", t.preconditions = "App installed.", t.steps = "1. Toggle off analytics.", t.expected_result = "Analytics stop.", t.test_type = "Compliance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-GLOB-COMP", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-045"}) ON CREATE SET t.description = "Validates that the Data Portability API successfully exports all user data in a machine-readable JSON format.", t.objective = "Verify Data Portability export.", t.preconditions = "User has data.", t.steps = "1. Call export API.", t.expected_result = "JSON downloaded.", t.test_type = "Compliance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-COMP", t.suite_id = "TS-GLOB-COMP", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-046"}) ON CREATE SET t.description = "Validates that the API Gateway enforces a rate limit of 100 requests per minute per user.", t.objective = "Verify API rate limiting.", t.preconditions = "API client.", t.steps = "1. Send 101 reqs/min.", t.expected_result = "429 response.", t.test_type = "Performance", t.priority = "High", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-PLAT-PERF", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-047"}) ON CREATE SET t.description = "Validates that read-heavy telemetry queries are correctly offloaded to database read replicas.", t.objective = "Verify read replica offloading.", t.preconditions = "DB access.", t.steps = "1. Run heavy read query.", t.expected_result = "Hits read replica.", t.test_type = "Performance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-PLAT-PERF", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-048"}) ON CREATE SET t.description = "Validates that static mobile app assets are served from the nearest global CDN edge location.", t.objective = "Verify CDN asset delivery.", t.preconditions = "Global network.", t.steps = "1. Request image from EU.", t.expected_result = "Served from EU edge.", t.test_type = "Performance", t.priority = "Medium", t.status = "Pass", t.owner = "QA-PERF", t.suite_id = "TS-PLAT-PERF", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-049"}) ON CREATE SET t.description = "Validates that core platform services are deployed across multiple Availability Zones.", t.objective = "Verify Multi-AZ deployment.", t.preconditions = "Cloud console.", t.steps = "1. Check deployment map.", t.expected_result = "Spread across AZs.", t.test_type = "Reliability", t.priority = "Critical", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-REL", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-050"}) ON CREATE SET t.description = "Validates that the database can be successfully restored to a specific point in time after simulated corruption.", t.objective = "Verify Point-in-Time Recovery.", t.preconditions = "DB backup enabled.", t.steps = "1. Corrupt data. 2. Restore.", t.expected_result = "Data restored.", t.test_type = "Reliability", t.priority = "Critical", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-REL", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-051"}) ON CREATE SET t.description = "Validates that the mobile app gracefully degrades and queues actions when cloud connectivity is lost.", t.objective = "Verify graceful degradation offline.", t.preconditions = "Block internet.", t.steps = "1. Perform action.", t.expected_result = "Action queued.", t.test_type = "Reliability", t.priority = "High", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-PLAT-REL", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-052"}) ON CREATE SET t.description = "Validates that application logs generated in microservices appear in the centralized logging dashboard.", t.objective = "Verify centralized log aggregation.", t.preconditions = "Logging dashboard.", t.steps = "1. Generate log.", t.expected_result = "Log appears.", t.test_type = "Observability", t.priority = "Medium", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-OBS", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-053"}) ON CREATE SET t.description = "Validates that automated alerts are triggered when API error rates exceed the 1% threshold.", t.objective = "Verify automated error alerting.", t.preconditions = "Alerting system.", t.steps = "1. Inject 500 errors.", t.expected_result = "Alert triggered.", t.test_type = "Observability", t.priority = "High", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-OBS", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-054"}) ON CREATE SET t.description = "Validates that distributed tracing correctly propagates trace IDs across all downstream services.", t.objective = "Verify distributed tracing.", t.preconditions = "Jaeger UI.", t.steps = "1. Make API call.", t.expected_result = "Trace ID visible.", t.test_type = "Observability", t.priority = "Medium", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-OBS", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-055"}) ON CREATE SET t.description = "Validates that telemetry records older than 90 days are automatically moved to cold storage.", t.objective = "Verify automated data lifecycle.", t.preconditions = "Cold storage enabled.", t.steps = "1. Insert old record.", t.expected_result = "Moves to cold.", t.test_type = "Data", t.priority = "Medium", t.status = "Pass", t.owner = "QA-OPS", t.suite_id = "TS-PLAT-DATA", t.plan_id = "STP-PLAT";
MERGE (t:TestCase {id: "TC-056"}) ON CREATE SET t.description = "Validates that time-based operations are stored in UTC and correctly converted to local timezones.", t.objective = "Verify UTC backend / local frontend.", t.preconditions = "Timezone settings.", t.steps = "1. Set Tokyo time.", t.expected_result = "Displays correctly.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-GLOB-LOC", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-057"}) ON CREATE SET t.description = "Validates that all API JSON responses strictly adhere to ISO 8601 date and time formatting.", t.objective = "Verify ISO 8601 API dates.", t.preconditions = "API client.", t.steps = "1. Check JSON dates.", t.expected_result = "Format correct.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-GLOB-LOC", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-058"}) ON CREATE SET t.description = "Validates that the mobile app UI dynamically updates to Japanese when the device OS language is changed.", t.objective = "Verify dynamic localization (Japanese).", t.preconditions = "Device set to JP.", t.steps = "1. Open App.", t.expected_result = "UI in Japanese.", t.test_type = "Functional", t.priority = "Medium", t.status = "Pass", t.owner = "QA-01", t.suite_id = "TS-GLOB-LOC", t.plan_id = "STP-GLOB";
MERGE (t:TestCase {id: "TC-059"}) ON CREATE SET t.description = "Validates that the mobile application and web dashboards meet WCAG 2.1 Level AA accessibility standards.", t.objective = "Verify WCAG 2.1 AA compliance.", t.preconditions = "Accessibility scanner.", t.steps = "1. Run axe-core.", t.expected_result = "Zero critical issues.", t.test_type = "Usability", t.priority = "High", t.status = "Pass", t.owner = "QA-UX", t.suite_id = "TS-PLAT-UX", t.plan_id = "STP-PLAT";

// --- 5. DIRECT RELATIONSHIPS ---
// 5.1 Parent-Child Decomposition
MATCH (c:Requirement {id: "REQ-L3-001"}), (p:Requirement {id: "REQ-L2-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-001"}), (p:Requirement {id: "REQ-L3-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-001"}), (p:Requirement {id: "REQ-L3-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-002"}), (p:Requirement {id: "REQ-L3-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-003"}), (p:Requirement {id: "REQ-L3-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-004"}), (p:Requirement {id: "REQ-L3-001"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-002"}), (p:Requirement {id: "REQ-L2-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-002"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-002"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-003"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-004"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-005"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-006"}), (p:Requirement {id: "REQ-L3-002"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-003"}), (p:Requirement {id: "REQ-L2-003"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-003"}), (p:Requirement {id: "REQ-L3-003"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-007"}), (p:Requirement {id: "REQ-L3-003"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-008"}), (p:Requirement {id: "REQ-L3-003"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-004"}), (p:Requirement {id: "REQ-L2-004"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-009"}), (p:Requirement {id: "REQ-L3-004"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-010"}), (p:Requirement {id: "REQ-L3-004"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-011"}), (p:Requirement {id: "REQ-L3-004"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-005"}), (p:Requirement {id: "REQ-L2-005"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-005"}), (p:Requirement {id: "REQ-L3-005"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-012"}), (p:Requirement {id: "REQ-L3-005"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-006"}), (p:Requirement {id: "REQ-L2-006"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-013"}), (p:Requirement {id: "REQ-L3-006"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-014"}), (p:Requirement {id: "REQ-L3-006"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-007"}), (p:Requirement {id: "REQ-L2-007"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-015"}), (p:Requirement {id: "REQ-L3-007"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-016"}), (p:Requirement {id: "REQ-L3-007"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-008"}), (p:Requirement {id: "REQ-L2-008"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-006"}), (p:Requirement {id: "REQ-L3-008"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-007"}), (p:Requirement {id: "REQ-L3-008"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-017"}), (p:Requirement {id: "REQ-L3-008"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-009"}), (p:Requirement {id: "REQ-L2-009"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-018"}), (p:Requirement {id: "REQ-L3-009"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-019"}), (p:Requirement {id: "REQ-L3-009"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-020"}), (p:Requirement {id: "REQ-L3-009"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-010"}), (p:Requirement {id: "REQ-L2-010"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-009"}), (p:Requirement {id: "REQ-L3-010"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-021"}), (p:Requirement {id: "REQ-L3-010"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-038"}), (p:Requirement {id: "REQ-L3-037"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-037"}), (p:Requirement {id: "REQ-L3-037"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L4-037"}), (p:Requirement {id: "REQ-L3-037"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L3-040"}), (p:Requirement {id: "REQ-L3-039"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-038"}), (p:Requirement {id: "REQ-L3-039"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-039"}), (p:Requirement {id: "REQ-L3-039"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-040"}), (p:Requirement {id: "REQ-L3-039"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-045"}), (p:Requirement {id: "REQ-L3-042"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);
MATCH (c:Requirement {id: "REQ-L5-046"}), (p:Requirement {id: "REQ-L3-042"})
MERGE (c)-[:CHILD_OF]->(p) MERGE (p)-[:PARENT_OF]->(c);

// 5.2 Component Allocation (ALLOCATED_TO)
MATCH (r:Requirement {id: "REQ-L2-001"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-001"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-001"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-001"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-002"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-003"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-004"}), (c:BusinessComponent {name: "Security Module"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-002"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-002"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-002"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-002"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-003"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-004"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-005"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-006"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-003"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-003"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-003"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-007"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-008"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-004"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-004"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-009"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-010"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-011"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-005"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-005"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-005"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-012"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-006"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-006"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-013"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-014"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-007"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-007"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-015"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-016"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-008"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-008"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-006"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-007"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-017"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-009"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-009"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-018"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-019"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-020"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L2-010"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-010"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-009"}), (c:BusinessComponent {name: "System"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-021"}), (c:BusinessComponent {name: "Vehicle Controller"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-037"}), (c:BusinessComponent {name: "Security Module"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-038"}), (c:BusinessComponent {name: "Security Module"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-037"}), (c:BusinessComponent {name: "Security Module"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-037"}), (c:BusinessComponent {name: "Security Module"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-039"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-040"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-038"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-039"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-040"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-038"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-039"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-041"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-040"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-041"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-041"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-042"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L4-042"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-043"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-044"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-042"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-045"}), (c:BusinessComponent {name: "Cloud Key Service"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L5-046"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);
MATCH (r:Requirement {id: "REQ-L3-043"}), (c:BusinessComponent {name: "Mobile App"})
MERGE (r)-[:ALLOCATED_TO]->(c);

// 5.3 Variant Targeting (TARGETS_VARIANT)
MATCH (r:Requirement {id: "REQ-L2-001"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-001"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-001"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-001"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-001"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-001"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-001"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-001"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-001"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-001"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-002"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-003"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-002"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-002"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-002"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-002"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-002"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-002"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-002"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-002"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-003"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-005"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-006"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-006"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-006"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-003"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-003"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-003"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-003"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-003"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-003"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-003"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-003"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-003"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-007"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-007"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-007"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-008"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-008"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-008"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-004"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-004"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-004"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-004"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-004"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-004"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-009"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-010"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-011"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-011"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-011"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-005"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-005"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-005"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-005"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-005"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-005"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-005"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-005"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-005"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-012"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-006"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-006"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-006"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-006"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-013"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-014"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-007"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-007"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-007"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-007"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-007"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-007"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-015"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-016"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-008"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-008"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-008"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-008"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-008"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-008"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-006"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-007"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-017"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-009"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-009"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-009"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-009"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-009"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-009"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-018"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-019"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-020"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-010"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-010"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L2-010"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-010"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-010"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-010"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-009"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-009"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-009"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-021"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-021"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-021"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-037"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-037"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-037"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-038"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-038"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-038"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-037"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-037"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-037"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-037"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-037"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-037"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-039"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-040"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-038"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-039"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-040"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-038"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-038"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-038"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-039"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-039"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-039"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-041"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-041"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-041"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-040"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-040"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-040"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-041"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-041"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-041"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-041"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-041"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-041"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-042"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-042"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-042"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-042"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-042"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L4-042"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-043"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-043"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-043"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-044"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-044"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-044"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-042"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-045"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L5-046"}), (v:Variant {id: "VAR-GLOB"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-043"}), (v:Variant {id: "VAR-BASE"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-043"}), (v:Variant {id: "VAR-PREM"})
MERGE (r)-[:TARGETS_VARIANT]->(v);
MATCH (r:Requirement {id: "REQ-L3-043"}), (v:Variant {id: "VAR-FLEET"})
MERGE (r)-[:TARGETS_VARIANT]->(v);

// 5.4 OEM Customization (CUSTOMIZED_FOR_OEM)
MATCH (r:Requirement {id: "REQ-L2-001"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-001"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-001"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-001"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-002"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-003"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-004"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-002"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-002"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-002"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-002"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-003"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-004"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-005"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-006"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-003"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-003"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-003"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-007"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-008"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-004"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-004"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-009"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-010"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-011"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-005"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-005"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-005"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-012"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-006"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-006"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-006"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-006"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-013"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-014"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-007"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-007"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-015"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-016"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-008"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-008"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-006"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-007"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-017"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-009"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-009"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-018"}), (o:OEM {name: "OEM-C"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-019"}), (o:OEM {name: "OEM-A"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-020"}), (o:OEM {name: "OEM-B"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L2-010"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-010"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-009"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-021"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-037"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-038"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-037"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-037"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-039"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-040"}), (o:OEM {name: "OEM-US"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-038"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-039"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-040"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-038"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-039"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-041"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-040"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-041"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-041"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-042"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L4-042"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-043"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-044"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-042"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-045"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L5-046"}), (o:OEM {name: "All Global OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);
MATCH (r:Requirement {id: "REQ-L3-043"}), (o:OEM {name: "All OEMs"})
MERGE (r)-[:CUSTOMIZED_FOR_OEM]->(o);

// 5.5 Artifact Type & Verification Level
MATCH (r:Requirement {id: "REQ-L2-001"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-001"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-001"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-001"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-001"}), (a:ArtifactType {name: "Detailed System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-001"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-001"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-001"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-002"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-002"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-003"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-003"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (a:ArtifactType {name: "Non-Functional Requirement (Security)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-002"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-002"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-002"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-002"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-002"}), (a:ArtifactType {name: "Detailed System Requirement (Performance)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-002"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-002"}), (a:ArtifactType {name: "Detailed System Requirement (Performance)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-002"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-003"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-003"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-004"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-004"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-005"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-005"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-006"}), (a:ArtifactType {name: "Non-Functional Requirement (Security)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-006"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-003"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-003"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-003"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-003"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-003"}), (a:ArtifactType {name: "Detailed System Requirement (Performance)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-003"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-007"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-007"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-008"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-008"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-004"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-004"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-004"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-004"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-009"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-009"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-010"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-010"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-011"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-011"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-005"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-005"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-005"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-005"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-005"}), (a:ArtifactType {name: "Detailed System Requirement (Performance)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-005"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-012"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-012"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-006"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-006"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-006"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-006"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-013"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-013"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-014"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-014"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-007"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-007"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-007"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-007"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-015"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-015"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-016"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-016"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-008"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-008"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-008"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-008"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-006"}), (a:ArtifactType {name: "Detailed System Requirement (Data)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-006"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-007"}), (a:ArtifactType {name: "Detailed System Requirement (Data)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-007"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-017"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-017"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-009"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-009"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-009"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-009"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-018"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-018"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-019"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-019"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-020"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-020"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L2-010"}), (a:ArtifactType {name: "Stakeholder Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L2-010"}), (v:VerificationLevel {name: "Acceptance"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-010"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-010"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-009"}), (a:ArtifactType {name: "Detailed System Requirement (Security)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-009"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-021"}), (a:ArtifactType {name: "Non-Functional Requirement (Security)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-021"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-037"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-037"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-038"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-038"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-037"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-037"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-037"}), (a:ArtifactType {name: "Detailed System Requirement (Security)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-037"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-039"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-039"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-040"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-040"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-038"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-038"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-039"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-039"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-040"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-040"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-038"}), (a:ArtifactType {name: "Detailed System Requirement (Performance)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-038"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-039"}), (a:ArtifactType {name: "Detailed System Requirement (Scalability)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-039"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-041"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-041"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-040"}), (a:ArtifactType {name: "Detailed System Requirement (Reliability)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-040"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-041"}), (a:ArtifactType {name: "Detailed System Requirement (Reliability)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-041"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-041"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-041"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-042"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-042"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L4-042"}), (a:ArtifactType {name: "Detailed System Requirement (Observability)"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L4-042"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-043"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-043"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-044"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-044"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-042"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-042"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-045"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-045"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L5-046"}), (a:ArtifactType {name: "Software Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L5-046"}), (v:VerificationLevel {name: "Integration"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);
MATCH (r:Requirement {id: "REQ-L3-043"}), (a:ArtifactType {name: "System Requirement"})
MERGE (r)-[:IS_OF_TYPE]->(a);
MATCH (r:Requirement {id: "REQ-L3-043"}), (v:VerificationLevel {name: "System"})
MERGE (r)-[:VERIFIED_AT_LEVEL]->(v);

// 5.6 Requirement-to-Test Traceability (VERIFIED_BY and VERIFIES)
MATCH (t:TestCase {id: "TC-ENR-001"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-002"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-003"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-004"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-005"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-006"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-006"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-007"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-007"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-ENR-008"}), (ts:TestSuite {id: "TS-FEAT-01"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-ENR-008"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-001"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-002"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-003"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-004"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-005"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-006"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-006"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-007"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-007"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-008"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-008"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-UNL-009"}), (ts:TestSuite {id: "TS-FEAT-02"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-UNL-009"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-001"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-002"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-003"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-004"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-005"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-RID-006"}), (ts:TestSuite {id: "TS-FEAT-03"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-RID-006"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SHR-001"}), (ts:TestSuite {id: "TS-FEAT-04"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SHR-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SHR-002"}), (ts:TestSuite {id: "TS-FEAT-04"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SHR-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SHR-003"}), (ts:TestSuite {id: "TS-FEAT-04"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SHR-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SHR-004"}), (ts:TestSuite {id: "TS-FEAT-04"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SHR-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SHR-005"}), (ts:TestSuite {id: "TS-FEAT-04"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SHR-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-REV-001"}), (ts:TestSuite {id: "TS-FEAT-05"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-REV-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-REV-002"}), (ts:TestSuite {id: "TS-FEAT-05"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-REV-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-REV-003"}), (ts:TestSuite {id: "TS-FEAT-05"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-REV-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-REV-004"}), (ts:TestSuite {id: "TS-FEAT-05"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-REV-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-PRF-001"}), (ts:TestSuite {id: "TS-FEAT-06"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-PRF-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-PRF-002"}), (ts:TestSuite {id: "TS-FEAT-06"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-PRF-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-PRF-003"}), (ts:TestSuite {id: "TS-FEAT-06"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-PRF-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-PRF-004"}), (ts:TestSuite {id: "TS-FEAT-06"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-PRF-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-VLT-001"}), (ts:TestSuite {id: "TS-FEAT-07"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-VLT-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-VLT-002"}), (ts:TestSuite {id: "TS-FEAT-07"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-VLT-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-VLT-003"}), (ts:TestSuite {id: "TS-FEAT-07"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-VLT-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-VLT-004"}), (ts:TestSuite {id: "TS-FEAT-07"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-VLT-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-001"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-002"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-003"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-004"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-005"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-SEC-006"}), (ts:TestSuite {id: "TS-FEAT-08"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-SEC-006"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-STS-001"}), (ts:TestSuite {id: "TS-FEAT-09"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-STS-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-STS-002"}), (ts:TestSuite {id: "TS-FEAT-09"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-STS-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-STS-003"}), (ts:TestSuite {id: "TS-FEAT-09"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-STS-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-STS-004"}), (ts:TestSuite {id: "TS-FEAT-09"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-STS-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-STS-005"}), (ts:TestSuite {id: "TS-FEAT-09"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-STS-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-OFF-001"}), (ts:TestSuite {id: "TS-FEAT-10"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-OFF-001"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-OFF-002"}), (ts:TestSuite {id: "TS-FEAT-10"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-OFF-002"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-OFF-003"}), (ts:TestSuite {id: "TS-FEAT-10"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-OFF-003"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-OFF-004"}), (ts:TestSuite {id: "TS-FEAT-10"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-OFF-004"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-OFF-005"}), (ts:TestSuite {id: "TS-FEAT-10"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-OFF-005"}), (tp:TestPlan {id: "STP-001"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-037"}), (ts:TestSuite {id: "TS-PLAT-SEC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-037"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-038"}), (ts:TestSuite {id: "TS-PLAT-SEC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-038"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-039"}), (ts:TestSuite {id: "TS-PLAT-SEC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-039"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-040"}), (ts:TestSuite {id: "TS-PLAT-SEC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-040"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-041"}), (ts:TestSuite {id: "TS-GLOB-COMP"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-041"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-042"}), (ts:TestSuite {id: "TS-GLOB-COMP"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-042"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-043"}), (ts:TestSuite {id: "TS-GLOB-COMP"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-043"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-044"}), (ts:TestSuite {id: "TS-GLOB-COMP"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-044"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-045"}), (ts:TestSuite {id: "TS-GLOB-COMP"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-045"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-046"}), (ts:TestSuite {id: "TS-PLAT-PERF"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-046"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-047"}), (ts:TestSuite {id: "TS-PLAT-PERF"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-047"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-048"}), (ts:TestSuite {id: "TS-PLAT-PERF"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-048"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-049"}), (ts:TestSuite {id: "TS-PLAT-REL"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-049"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-050"}), (ts:TestSuite {id: "TS-PLAT-REL"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-050"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-051"}), (ts:TestSuite {id: "TS-PLAT-REL"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-051"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-052"}), (ts:TestSuite {id: "TS-PLAT-OBS"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-052"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-053"}), (ts:TestSuite {id: "TS-PLAT-OBS"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-053"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-054"}), (ts:TestSuite {id: "TS-PLAT-OBS"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-054"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-055"}), (ts:TestSuite {id: "TS-PLAT-DATA"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-055"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-056"}), (ts:TestSuite {id: "TS-GLOB-LOC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-056"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-057"}), (ts:TestSuite {id: "TS-GLOB-LOC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-057"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-058"}), (ts:TestSuite {id: "TS-GLOB-LOC"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-058"}), (tp:TestPlan {id: "STP-GLOB"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (t:TestCase {id: "TC-059"}), (ts:TestSuite {id: "TS-PLAT-UX"})
MERGE (t)-[:BELONGS_TO_SUITE]->(ts);
MATCH (t:TestCase {id: "TC-059"}), (tp:TestPlan {id: "STP-PLAT"})
MERGE (t)-[:BELONGS_TO_PLAN]->(tp);
MATCH (r:Requirement {id: "REQ-L2-001"}), (t:TestCase {id: "TC-ENR-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-001"}), (t:TestCase {id: "TC-ENR-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-002"}), (t:TestCase {id: "TC-UNL-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-002"}), (t:TestCase {id: "TC-UNL-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-003"}), (t:TestCase {id: "TC-RID-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-004"}), (t:TestCase {id: "TC-SHR-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-005"}), (t:TestCase {id: "TC-REV-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-006"}), (t:TestCase {id: "TC-PRF-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-007"}), (t:TestCase {id: "TC-VLT-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-008"}), (t:TestCase {id: "TC-SEC-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-009"}), (t:TestCase {id: "TC-STS-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L2-010"}), (t:TestCase {id: "TC-OFF-001"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-001"}), (t:TestCase {id: "TC-ENR-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-002"}), (t:TestCase {id: "TC-UNL-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-003"}), (t:TestCase {id: "TC-RID-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-003"}), (t:TestCase {id: "TC-RID-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-004"}), (t:TestCase {id: "TC-SHR-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-005"}), (t:TestCase {id: "TC-REV-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-006"}), (t:TestCase {id: "TC-PRF-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-007"}), (t:TestCase {id: "TC-VLT-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-008"}), (t:TestCase {id: "TC-SEC-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-008"}), (t:TestCase {id: "TC-SEC-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-009"}), (t:TestCase {id: "TC-STS-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-010"}), (t:TestCase {id: "TC-OFF-002"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-010"}), (t:TestCase {id: "TC-OFF-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-037"}), (t:TestCase {id: "TC-037"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-038"}), (t:TestCase {id: "TC-038"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-039"}), (t:TestCase {id: "TC-041"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-040"}), (t:TestCase {id: "TC-042"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-041"}), (t:TestCase {id: "TC-051"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-042"}), (t:TestCase {id: "TC-056"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L3-043"}), (t:TestCase {id: "TC-059"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-001"}), (t:TestCase {id: "TC-ENR-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-002"}), (t:TestCase {id: "TC-UNL-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-002"}), (t:TestCase {id: "TC-UNL-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-003"}), (t:TestCase {id: "TC-RID-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-003"}), (t:TestCase {id: "TC-UNL-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-005"}), (t:TestCase {id: "TC-REV-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-006"}), (t:TestCase {id: "TC-SEC-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-007"}), (t:TestCase {id: "TC-SEC-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-007"}), (t:TestCase {id: "TC-SEC-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-007-FLEET"}), (t:TestCase {id: "TC-SEC-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-008"}), (t:TestCase {id: "TC-SEC-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-009"}), (t:TestCase {id: "TC-OFF-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-037"}), (t:TestCase {id: "TC-040"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-038"}), (t:TestCase {id: "TC-046"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-039"}), (t:TestCase {id: "TC-047"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-040"}), (t:TestCase {id: "TC-049"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-041"}), (t:TestCase {id: "TC-050"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L4-042"}), (t:TestCase {id: "TC-053"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-001"}), (t:TestCase {id: "TC-ENR-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-002"}), (t:TestCase {id: "TC-ENR-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-003"}), (t:TestCase {id: "TC-ENR-007"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-003"}), (t:TestCase {id: "TC-UNL-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-004"}), (t:TestCase {id: "TC-ENR-008"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-004"}), (t:TestCase {id: "TC-UNL-007"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-005"}), (t:TestCase {id: "TC-UNL-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-005"}), (t:TestCase {id: "TC-UNL-008"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-006"}), (t:TestCase {id: "TC-UNL-007"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-006"}), (t:TestCase {id: "TC-UNL-009"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-007"}), (t:TestCase {id: "TC-RID-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-007"}), (t:TestCase {id: "TC-UNL-008"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-008"}), (t:TestCase {id: "TC-RID-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-008"}), (t:TestCase {id: "TC-UNL-009"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-009"}), (t:TestCase {id: "TC-RID-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-009"}), (t:TestCase {id: "TC-SHR-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-010"}), (t:TestCase {id: "TC-RID-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-010"}), (t:TestCase {id: "TC-SHR-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-011"}), (t:TestCase {id: "TC-SHR-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-011"}), (t:TestCase {id: "TC-SHR-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-012"}), (t:TestCase {id: "TC-REV-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-012"}), (t:TestCase {id: "TC-SHR-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-013"}), (t:TestCase {id: "TC-PRF-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-013"}), (t:TestCase {id: "TC-SHR-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-014"}), (t:TestCase {id: "TC-PRF-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-015"}), (t:TestCase {id: "TC-REV-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-015"}), (t:TestCase {id: "TC-VLT-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-016"}), (t:TestCase {id: "TC-VLT-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-017"}), (t:TestCase {id: "TC-PRF-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-017"}), (t:TestCase {id: "TC-SEC-006"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-018"}), (t:TestCase {id: "TC-PRF-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-018"}), (t:TestCase {id: "TC-STS-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-019"}), (t:TestCase {id: "TC-STS-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-020"}), (t:TestCase {id: "TC-STS-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-020"}), (t:TestCase {id: "TC-VLT-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-021"}), (t:TestCase {id: "TC-OFF-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-021"}), (t:TestCase {id: "TC-VLT-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-024"}), (t:TestCase {id: "TC-STS-003"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-025"}), (t:TestCase {id: "TC-STS-004"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-026"}), (t:TestCase {id: "TC-OFF-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-026"}), (t:TestCase {id: "TC-STS-005"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-037"}), (t:TestCase {id: "TC-039"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-038"}), (t:TestCase {id: "TC-043"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-039"}), (t:TestCase {id: "TC-044"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-040"}), (t:TestCase {id: "TC-045"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-041"}), (t:TestCase {id: "TC-048"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-042"}), (t:TestCase {id: "TC-052"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-043"}), (t:TestCase {id: "TC-054"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-044"}), (t:TestCase {id: "TC-055"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-045"}), (t:TestCase {id: "TC-057"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);
MATCH (r:Requirement {id: "REQ-L5-046"}), (t:TestCase {id: "TC-058"})
MERGE (r)-[:VERIFIED_BY]->(t)
MERGE (t)-[:VERIFIES]->(r);

// ===========================================================================
// --- 6. DYNAMIC SEMANTIC RELATIONSHIPS ---
// ===========================================================================

// 6.1 Variant Divergence (Sibling requirements targeting alternate variants)
MATCH (r1:Requirement {id: "REQ-L4-001"}), (r2:Requirement {id: "REQ-L5-001"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-BASE]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-BASE]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-001"}), (r2:Requirement {id: "REQ-L5-002"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-001"}), (r2:Requirement {id: "REQ-L5-003"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-001"}), (r2:Requirement {id: "REQ-L5-002"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-001"}), (r2:Requirement {id: "REQ-L5-003"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-001"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-002"}), (r2:Requirement {id: "REQ-L5-003"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-002"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-FLEET] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-001", rationale: "Variant divergence under REQ-L3-001: [VAR-FLEET] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L4-002"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-003"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-002"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-005"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-FLEET] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-002", rationale: "Variant divergence under REQ-L3-002: [VAR-FLEET] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-009"}), (r2:Requirement {id: "REQ-L5-010"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-009"}), (r2:Requirement {id: "REQ-L5-011"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-BASE] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-010"}), (r2:Requirement {id: "REQ-L5-011"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-004", rationale: "Variant divergence under REQ-L3-004: [VAR-PREM] vs [VAR-BASE, VAR-PREM, VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-005"}), (r2:Requirement {id: "REQ-L5-012"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-005", rationale: "Variant divergence under REQ-L3-005: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-005", rationale: "Variant divergence under REQ-L3-005: [VAR-BASE, VAR-PREM, VAR-FLEET] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-013"}), (r2:Requirement {id: "REQ-L5-014"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-006", rationale: "Variant divergence under REQ-L3-006: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-006", rationale: "Variant divergence under REQ-L3-006: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-015"}), (r2:Requirement {id: "REQ-L5-016"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-007", rationale: "Variant divergence under REQ-L3-007: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-007", rationale: "Variant divergence under REQ-L3-007: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-006"}), (r2:Requirement {id: "REQ-L4-007"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-006"}), (r2:Requirement {id: "REQ-L5-017"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-BASE] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-BASE] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-007"}), (r2:Requirement {id: "REQ-L5-017"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-008", rationale: "Variant divergence under REQ-L3-008: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-018"}), (r2:Requirement {id: "REQ-L5-019"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-BASE] vs [VAR-PREM]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-BASE] vs [VAR-PREM]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-018"}), (r2:Requirement {id: "REQ-L5-020"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-BASE] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-BASE] vs [VAR-FLEET]"}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-019"}), (r2:Requirement {id: "REQ-L5-020"})
MERGE (r1)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-PREM] vs [VAR-FLEET]"}]->(r2)
MERGE (r2)-[:VARIANT_DIVERGENCE_OF {parent: "REQ-L3-009", rationale: "Variant divergence under REQ-L3-009: [VAR-PREM] vs [VAR-FLEET]"}]->(r1);

// 6.2 Component Co-Allocation
MATCH (r1:Requirement {id: "REQ-L5-001"}), (r2:Requirement {id: "REQ-L5-002"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-002"}), (r2:Requirement {id: "REQ-L5-007"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-007"}), (r2:Requirement {id: "REQ-L5-011"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-011"}), (r2:Requirement {id: "REQ-L5-013"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-013"}), (r2:Requirement {id: "REQ-L5-018"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-018"}), (r2:Requirement {id: "REQ-L5-019"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-019"}), (r2:Requirement {id: "REQ-L5-039"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-039"}), (r2:Requirement {id: "REQ-L3-041"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-041"}), (r2:Requirement {id: "REQ-L5-046"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-046"}), (r2:Requirement {id: "REQ-L3-043"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Mobile App"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L3-004"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-004"}), (r2:Requirement {id: "REQ-L5-009"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-009"}), (r2:Requirement {id: "REQ-L5-010"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-010"}), (r2:Requirement {id: "REQ-L5-012"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-012"}), (r2:Requirement {id: "REQ-L5-014"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-014"}), (r2:Requirement {id: "REQ-L3-007"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-007"}), (r2:Requirement {id: "REQ-L4-006"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L4-006"}), (r2:Requirement {id: "REQ-L4-007"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L4-007"}), (r2:Requirement {id: "REQ-L5-017"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-017"}), (r2:Requirement {id: "REQ-L5-020"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-020"}), (r2:Requirement {id: "REQ-L3-039"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-039"}), (r2:Requirement {id: "REQ-L3-040"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Cloud Key Service"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L3-037"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Security Module"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-037"}), (r2:Requirement {id: "REQ-L3-038"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Security Module"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L3-038"}), (r2:Requirement {id: "REQ-L5-037"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Security Module"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-037"}), (r2:Requirement {id: "REQ-L4-037"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Security Module"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-005"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-006"}), (r2:Requirement {id: "REQ-L5-008"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-008"}), (r2:Requirement {id: "REQ-L5-015"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-015"}), (r2:Requirement {id: "REQ-L5-016"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);
MATCH (r1:Requirement {id: "REQ-L5-016"}), (r2:Requirement {id: "REQ-L5-021"})
MERGE (r1)-[:CO_ALLOCATED_WITH {component: "Vehicle Controller"}]->(r2);

// 6.3 Semantic Domain Affinity
MATCH (r1:Requirement {id: "REQ-L5-001"}), (r2:Requirement {id: "REQ-L5-003"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "ble", score: 0.273}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "ble", score: 0.273}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-004"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.304}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.304}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L3-002"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.143}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.143}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.208}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.208}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-003"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.185}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.185}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L3-002"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.133}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.133}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L4-002"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "uwb", score: 0.192}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "uwb", score: 0.192}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.192}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.192}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-004"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.172}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.172}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-002"}), (r2:Requirement {id: "REQ-L5-005"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.138}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.138}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-002"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.125}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.125}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-002"}), (r2:Requirement {id: "REQ-L3-009"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.161}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.161}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-005"}), (r2:Requirement {id: "REQ-L5-006"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.179}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.179}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-005"}), (r2:Requirement {id: "REQ-L5-014"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.143}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "unlock", score: 0.143}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-005"}), (r2:Requirement {id: "REQ-L4-005"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "revocation", score: 0.222}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "revocation", score: 0.222}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-005"}), (r2:Requirement {id: "REQ-L5-012"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "revocation", score: 0.125}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "revocation", score: 0.125}]->(r1);
MATCH (r1:Requirement {id: "REQ-L2-007"}), (r2:Requirement {id: "REQ-L5-015"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "valet", score: 0.138}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "valet", score: 0.138}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-015"}), (r2:Requirement {id: "REQ-L5-016"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "speed", score: 0.4}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "speed", score: 0.4}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-009"}), (r2:Requirement {id: "REQ-L5-018"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.24}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.24}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-009"}), (r2:Requirement {id: "REQ-L5-019"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.185}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.185}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-009"}), (r2:Requirement {id: "REQ-L5-020"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "telemetry", score: 0.143}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "telemetry", score: 0.143}]->(r1);
MATCH (r1:Requirement {id: "REQ-L5-018"}), (r2:Requirement {id: "REQ-L5-019"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.227}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "lock", score: 0.227}]->(r1);
MATCH (r1:Requirement {id: "REQ-L2-010"}), (r2:Requirement {id: "REQ-L3-010"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.182}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.182}]->(r1);
MATCH (r1:Requirement {id: "REQ-L2-010"}), (r2:Requirement {id: "REQ-L4-009"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.148}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.148}]->(r1);
MATCH (r1:Requirement {id: "REQ-L2-010"}), (r2:Requirement {id: "REQ-L5-021"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.062}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.062}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-010"}), (r2:Requirement {id: "REQ-L4-009"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.286}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.286}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-010"}), (r2:Requirement {id: "REQ-L5-021"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.147}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.147}]->(r1);
MATCH (r1:Requirement {id: "REQ-L4-009"}), (r2:Requirement {id: "REQ-L5-021"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.148}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "grace, offline", score: 0.148}]->(r1);
MATCH (r1:Requirement {id: "REQ-L3-037"}), (r2:Requirement {id: "REQ-L3-038"})
MERGE (r1)-[:SEMANTIC_AFFINITY {shared_topics: "encryption", score: 0.25}]->(r2)
MERGE (r2)-[:SEMANTIC_AFFINITY {shared_topics: "encryption", score: 0.25}]->(r1);

// --- 7. Verification Summary Queries ---
MATCH (n) RETURN labels(n) as EntityType, count(*) as NodeCount ORDER BY NodeCount DESC;
MATCH ()-[r]->() RETURN type(r) as RelationshipType, count(*) as EdgeCount ORDER BY EdgeCount DESC;