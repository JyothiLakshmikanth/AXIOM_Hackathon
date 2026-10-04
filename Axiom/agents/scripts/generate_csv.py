import csv

# ==========================================
# 1. MASTER REQUIREMENTS (V5 - Full Depth + Variant Divergence)
# ==========================================
requirements_data = [
    ["Requirement ID", "Artifact Type", "Primary Text", "Verification Criteria", "Verification Level", "Test Cases Linked", "Parent Requirement", "Status", "Target Variant", "Level", "Business Component", "Variant Implementation Notes", "OEM Customization Flag"],

    # ================= FEAT-01: Digital Key Enrollment =================
    ["REQ-L2-001", "Stakeholder Requirement", "The vehicle owner shall be able to securely pair their smartphone with the electric two-wheeler to enable digital key functionality.", "Demonstration: Show successful pairing process.", "Acceptance", "TC-ENR-001, TC-ENR-002", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core feature across all variants.", "All OEMs"],
    ["REQ-L3-001", "System Requirement", "The E-Key 2W system shall support the secure provisioning of a digital key from the mobile application to the vehicle-side controller via the cloud lifecycle service.", "Test: Verify end-to-end key provisioning flow.", "System", "TC-ENR-003", "REQ-L2-001", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Standard cloud lifecycle.", "All OEMs"],
    ["REQ-L4-001", "Detailed System Requirement", "The digital key enrollment process shall complete within 15 seconds under nominal network conditions.", "Test: Measure end-to-end enrollment time over 20 runs.", "System", "TC-ENR-004", "REQ-L3-001", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "System", "Standard latency bound.", "All OEMs"],
    ["REQ-L5-001", "Software Requirement", "The Base mobile app shall discover an eligible vehicle via standard BLE and initiate enrollment.", "Test: Verify BLE discovery and enrollment initiation.", "Integration", "TC-ENR-005", "REQ-L3-001", "Draft", "VAR-BASE", "L5", "Mobile App", "BLE only discovery.", "OEM-C"],
    ["REQ-L5-002", "Software Requirement", "The Premium mobile app shall require on-device biometric authentication before initiating enrollment.", "Test: Verify biometric prompt blocks enrollment if failed.", "Integration", "TC-ENR-006", "REQ-L3-001", "Draft", "VAR-PREM", "L5", "Mobile App", "FaceID/TouchID integration.", "OEM-A"],
    ["REQ-L5-003", "Software Requirement", "The Fleet cloud service shall support bulk CSV upload for provisioning up to 10,000 keys simultaneously.", "Test: Upload 10k CSV and verify provisioning success rate.", "Integration", "TC-ENR-007", "REQ-L3-001", "Draft", "VAR-FLEET", "L5", "Cloud Key Service", "Batch processing pipeline.", "OEM-B"],
    ["REQ-L5-004", "Non-Functional Requirement (Security)", "The system shall require authenticated owner identity before provisioning a digital key.", "Test: Verify unauthenticated user cannot provision key.", "System", "TC-ENR-008", "REQ-L3-001", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Security Module", "OAuth2/JWT enforcement.", "All OEMs"],

    # ================= FEAT-02: Passive Unlock/Lock =================
    ["REQ-L2-002", "Stakeholder Requirement", "The rider shall experience seamless, hands-free unlocking and locking of the vehicle based on their physical proximity.", "Demonstration: Show vehicle unlocking as phone approaches.", "Acceptance", "TC-UNL-001, TC-UNL-002", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core feature, implementation varies.", "All OEMs"],
    ["REQ-L3-002", "System Requirement", "The system shall automatically unlock or lock the vehicle when an authorized smartphone enters or leaves the defined proximity zone.", "Test: Verify proximity-based unlock and lock actions.", "System", "TC-UNL-003", "REQ-L2-002", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Proximity policy engine.", "All OEMs"],
    ["REQ-L4-002", "Detailed System Requirement (Performance)", "The Base variant end-to-end unlock decision shall complete within 1.5 seconds under nominal conditions.", "Test: Measure BLE unlock latency over 50 runs.", "System", "TC-UNL-004", "REQ-L3-002", "Draft", "VAR-BASE", "L4", "System", "BLE RSSI processing time.", "OEM-C"],
    ["REQ-L4-002", "Detailed System Requirement (Performance)", "The Premium variant UWB secure ranging handshake shall complete within 800ms.", "Test: Measure UWB handshake latency over 50 runs.", "System", "TC-UNL-005", "REQ-L3-002", "Draft", "VAR-PREM", "L4", "System", "UWB IEEE 802.15.4z latency.", "OEM-A"],
    ["REQ-L5-003", "Software Requirement", "The Base vehicle controller shall unlock using standard BLE RSSI thresholds (-65 dBm).", "Test: Verify BLE RSSI triggers unlock.", "Integration", "TC-UNL-006", "REQ-L3-002", "Draft", "VAR-BASE", "L5", "Vehicle Controller", "BLE only.", "OEM-C"],
    ["REQ-L5-004", "Software Requirement", "The Premium vehicle controller shall unlock using UWB precise ranging to prevent relay attacks.", "Test: Verify UWB triggers unlock and rejects relay attacks.", "Integration", "TC-UNL-007", "REQ-L3-002", "Draft", "VAR-PREM", "L5", "Vehicle Controller", "UWB secure ranging.", "OEM-A"],
    ["REQ-L5-005", "Software Requirement", "The Fleet vehicle controller shall accept remote unlock commands from the Fleet Dispatcher API.", "Test: Verify Fleet API remote unlock command actuates mechanism.", "Integration", "TC-UNL-008", "REQ-L3-002", "Draft", "VAR-FLEET", "L5", "Vehicle Controller", "MQTT remote command.", "OEM-B"],
    ["REQ-L5-006", "Non-Functional Requirement (Security)", "The vehicle controller shall immediately reject unlock requests from an unrecognized digital key identifier.", "Test: Unknown phone attempts to unlock; verify rejection.", "System", "TC-UNL-009", "REQ-L3-002", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Vehicle Controller", "Crypto ID validation.", "All OEMs"],

    # ================= FEAT-03: Ride Authorization =================
    ["REQ-L2-003", "Stakeholder Requirement", "The system shall ensure that only authorized riders with valid permissions can start and ride the vehicle.", "Analysis: Review security architecture.", "Acceptance", "TC-RID-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core security feature.", "All OEMs"],
    ["REQ-L3-003", "System Requirement", "The system shall permit ride authorization only when the presented digital key is cryptographically valid, active, and not revoked.", "Test: Verify valid key permits ride, revoked key is rejected.", "System", "TC-RID-002, TC-RID-003", "REQ-L2-003", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Real-time validation.", "All OEMs"],
    ["REQ-L4-003", "Detailed System Requirement (Performance)", "The vehicle ignition enable signal shall be triggered within 500ms of the mobile app sending the 'Ready to Ride' command.", "Test: Measure time between app command and ignition relay.", "System", "TC-RID-004", "REQ-L3-003", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "System", "Ignition relay latency.", "All OEMs"],
    ["REQ-L5-007", "Software Requirement", "The mobile application shall provide a clear UI indicator showing whether ride authorization is currently active.", "Test: Verify rider can view active ride authorization status.", "Integration", "TC-RID-005", "REQ-L3-003", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Mobile App", "UI state management.", "All OEMs"],
    ["REQ-L5-008", "Software Requirement", "The vehicle controller shall execute a cryptographic challenge-response handshake before enabling ignition.", "Test: Verify ignition is disabled if crypto handshake fails.", "Integration", "TC-RID-006", "REQ-L3-003", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Vehicle Controller", "AES-256 challenge-response.", "All OEMs"],

    # ================= FEAT-04: Key Sharing =================
    ["REQ-L2-004", "Stakeholder Requirement", "The vehicle owner shall be able to share constrained, temporary digital key access with other riders securely.", "Demonstration: Show owner creating a shared key.", "Acceptance", "TC-SHR-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core sharing feature.", "All OEMs"],
    ["REQ-L3-004", "System Requirement", "The cloud key lifecycle service shall allow an owner to generate and distribute a shared digital key with configurable constraints.", "Test: Verify shared key expires and respects permissions.", "System", "TC-SHR-002", "REQ-L2-004", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Cloud Key Service", "Constraint engine.", "All OEMs"],
    ["REQ-L5-009", "Software Requirement", "The Base cloud service shall enforce time-based expiry constraints on shared keys.", "Test: Verify shared key expires at configured time.", "Integration", "TC-SHR-003", "REQ-L3-004", "Draft", "VAR-BASE", "L5", "Cloud Key Service", "Time-based ACL.", "OEM-C"],
    ["REQ-L5-010", "Software Requirement", "The Premium cloud service shall enforce geofencing constraints on shared keys.", "Test: Verify shared key fails if used outside defined geo-zone.", "Integration", "TC-SHR-004", "REQ-L3-004", "Draft", "VAR-PREM", "L5", "Cloud Key Service", "Geo-fencing ACL.", "OEM-A"],
    ["REQ-L5-011", "Software Requirement", "The mobile application shall display a list of all currently active shared keys and their constraints.", "Test: Verify owner sees active shared keys list.", "Integration", "TC-SHR-005", "REQ-L3-004", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Mobile App", "List UI component.", "All OEMs"],

    # ================= FEAT-05: Key Revocation =================
    ["REQ-L2-005", "Stakeholder Requirement", "The vehicle owner shall have the ability to instantly revoke digital key access in case of loss or theft.", "Demonstration: Show owner revoking a key.", "Acceptance", "TC-REV-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Critical security feature.", "All OEMs"],
    ["REQ-L3-005", "System Requirement", "The system shall support immediate revocation of a shared digital key, propagating status to vehicle and mobile.", "Test: Verify owner can revoke and measure propagation time.", "System", "TC-REV-002", "REQ-L2-005", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "CRL propagation.", "All OEMs"],
    ["REQ-L4-005", "Detailed System Requirement (Performance)", "A revocation command received by the vehicle online shall become effective within 10 seconds.", "Test: Measure online revocation propagation time.", "System", "TC-REV-003", "REQ-L3-005", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "System", "Propagation latency.", "All OEMs"],
    ["REQ-L5-012", "Software Requirement", "The Fleet cloud service shall support bulk API revocation for up to 1,000 keys simultaneously.", "Test: Verify bulk API revokes 1k keys within 30s.", "Integration", "TC-REV-004", "REQ-L3-005", "Draft", "VAR-FLEET", "L5", "Cloud Key Service", "Bulk batch processing.", "OEM-B"],

    # ================= FEAT-06: Rider Profiles =================
    ["REQ-L2-006", "Stakeholder Requirement", "The system shall allow owners to customize rider access based on specific time windows or usage restrictions.", "Analysis: Review UI/UX and permission schemas.", "Acceptance", "TC-PRF-001", "None", "Accepted", "VAR-PREM, VAR-FLEET", "L2", "System", "Premium/Fleet only feature.", "OEM-A, OEM-B"],
    ["REQ-L3-006", "System Requirement", "The system shall support the configuration and enforcement of rider profiles, including time-window access.", "Test: Verify rider access is denied outside time window.", "System", "TC-PRF-002", "REQ-L2-006", "Draft", "VAR-PREM, VAR-FLEET", "L3", "System", "Policy engine.", "OEM-A, OEM-B"],
    ["REQ-L5-013", "Software Requirement", "The Premium mobile app shall allow the owner to restrict a specific rider's access to a configured time window.", "Test: Verify owner can set and save time window.", "Integration", "TC-PRF-003", "REQ-L3-006", "Draft", "VAR-PREM", "L5", "Mobile App", "Time-picker UI.", "OEM-A"],
    ["REQ-L5-014", "Software Requirement", "The Fleet Dashboard shall allow admins to assign shift-based profiles to riders.", "Test: Verify rider can only unlock during assigned shift.", "Integration", "TC-PRF-004", "REQ-L3-006", "Draft", "VAR-FLEET", "L5", "Cloud Key Service", "Shift management integration.", "OEM-B"],

    # ================= FEAT-07: Valet & Service Mode =================
    ["REQ-L2-007", "Stakeholder Requirement", "The system shall provide a secure, temporary access mode for valet or service personnel.", "Demonstration: Show creation and usage of a temporary service key.", "Acceptance", "TC-VLT-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core feature.", "All OEMs"],
    ["REQ-L3-007", "System Requirement", "The system shall allow the generation of a temporary service key with predefined, limited permissions.", "Test: Verify temporary service key works only with restricted permissions.", "System", "TC-VLT-002", "REQ-L2-007", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Cloud Key Service", "Permission masking.", "All OEMs"],
    ["REQ-L5-015", "Software Requirement", "The Base vehicle controller shall limit max speed to 20km/h when a service key is active.", "Test: Verify speed is limited under valet mode.", "Integration", "TC-VLT-003", "REQ-L3-007", "Draft", "VAR-BASE", "L5", "Vehicle Controller", "Speed limiter logic.", "OEM-C"],
    ["REQ-L5-016", "Software Requirement", "The Premium vehicle controller shall disable trunk release and limit speed when a service key is active.", "Test: Verify trunk disabled and speed limited.", "Integration", "TC-VLT-004", "REQ-L3-007", "Draft", "VAR-PREM", "L5", "Vehicle Controller", "Advanced permission masking.", "OEM-A"],

    # ================= FEAT-08: Security & Event Monitoring =================
    ["REQ-L2-008", "Stakeholder Requirement", "The system shall maintain a secure, auditable log of all security-relevant events.", "Inspection: Review security event log schema.", "Acceptance", "TC-SEC-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Compliance feature.", "All OEMs"],
    ["REQ-L3-008", "System Requirement", "The system shall record all failed authorization attempts and expose them only to authorized users.", "Test: Verify failed attempts create event and unauthorized users cannot read.", "System", "TC-SEC-002, TC-SEC-003", "REQ-L2-008", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Audit logging.", "All OEMs"],
    ["REQ-L4-006", "Detailed System Requirement (Data)", "The Base variant shall retain security logs for a minimum of 1 year.", "Inspection: Verify cloud DB retention policy.", "System", "TC-SEC-004", "REQ-L3-008", "Draft", "VAR-BASE", "L4", "Cloud Key Service", "Cost-optimized retention.", "OEM-C"],
    ["REQ-L4-007", "Detailed System Requirement (Data)", "The Premium variant shall retain high-fidelity telemetry and security logs for 5 years immutably.", "Inspection: Verify Data Lake retention and WORM policy.", "System", "TC-SEC-005", "REQ-L3-008", "Draft", "VAR-PREM", "L4", "Cloud Key Service", "Premium compliance tier.", "OEM-A"],
    ["REQ-L5-017", "Software Requirement", "The Fleet variant shall stream security events to external SIEM systems via Webhook.", "Test: Verify SIEM receives formatted security events.", "Integration", "TC-SEC-006", "REQ-L3-008", "Draft", "VAR-FLEET", "L5", "Cloud Key Service", "SIEM integration.", "OEM-B"],

    # ================= FEAT-09: Vehicle Status =================
    ["REQ-L2-009", "Stakeholder Requirement", "The user shall be able to remotely check the basic status of the vehicle.", "Demonstration: Show app displaying accurate status.", "Acceptance", "TC-STS-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Core feature.", "All OEMs"],
    ["REQ-L3-009", "System Requirement", "The system shall periodically synchronize and display the vehicle's latest known connection status and battery.", "Test: Verify app shows latest lock state and battery.", "System", "TC-STS-002", "REQ-L2-009", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Telemetry sync.", "All OEMs"],
    ["REQ-L5-018", "Software Requirement", "The Base app shall display lock state via standard REST polling every 60s.", "Test: Verify app UI reflects lock state.", "Integration", "TC-STS-003", "REQ-L3-009", "Draft", "VAR-BASE", "L5", "Mobile App", "REST polling.", "OEM-C"],
    ["REQ-L5-019", "Software Requirement", "The Premium app shall receive real-time lock state updates via WebSockets.", "Test: Verify app updates instantly on lock change.", "Integration", "TC-STS-004", "REQ-L3-009", "Draft", "VAR-PREM", "L5", "Mobile App", "WebSocket push.", "OEM-A"],
    ["REQ-L5-020", "Software Requirement", "The Fleet Dashboard shall display real-time telemetry for 10k vehicles via WebSockets.", "Test: Verify dashboard updates 10k pins within 5s.", "Integration", "TC-STS-005", "REQ-L3-009", "Draft", "VAR-FLEET", "L5", "Cloud Key Service", "High-scale WebSockets.", "OEM-B"],

    # ================= FEAT-10: Offline Grace Mode =================
    ["REQ-L2-010", "Stakeholder Requirement", "The vehicle shall remain operable for a limited period if cloud connectivity is temporarily lost.", "Analysis: Review offline grace period risk assessment.", "Acceptance", "TC-OFF-001", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L2", "System", "Resilience feature.", "All OEMs"],
    ["REQ-L3-010", "System Requirement", "The system shall support a limited offline grace period, allowing ride authorization without real-time cloud validation.", "Test: Verify vehicle permits offline grace and rejects after expiry.", "System", "TC-OFF-002, TC-OFF-003", "REQ-L2-010", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "System", "Offline cache logic.", "All OEMs"],
    ["REQ-L4-009", "Detailed System Requirement (Security)", "The maximum allowable offline grace period shall be 72 hours.", "Test: Simulate 73 hours offline; verify vehicle rejects ride.", "System", "TC-OFF-004", "REQ-L3-010", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "System", "Security bound.", "All OEMs"],
    ["REQ-L5-021", "Non-Functional Requirement (Security)", "The offline grace mode shall strictly terminate when its configured validity window expires.", "Test: Verify expired offline grace is rejected.", "Integration", "TC-OFF-005", "REQ-L3-010", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Vehicle Controller", "Hard timeout logic.", "All OEMs"],

    # ================= PLATFORM & GLOBAL (Cross-Cutting - Clean IDs) =================
    
    # --- Security & Compliance ---
    ["REQ-L3-037", "System Requirement", "The platform shall enforce TLS 1.3 encryption for all data in transit.", "Inspection: Review network captures for TLS 1.3.", "System", "TC-037", "None", "Accepted", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Security Module", "Platform baseline.", "All OEMs"],
    ["REQ-L3-038", "System Requirement", "The platform shall enforce AES-256 encryption for all sensitive data at rest in databases and object storage.", "Inspection: Verify database and S3/GCS bucket encryption settings.", "System", "TC-038", "REQ-L3-037", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Security Module", "SOC2/ISO27001 baseline.", "All OEMs"],
    ["REQ-L5-037", "Software Requirement", "The platform shall manage all API keys, database credentials, and cryptographic seeds via a centralized secrets manager.", "Test: Verify no hardcoded secrets exist in source code or environment variables.", "Integration", "TC-039", "REQ-L3-037", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Security Module", "Zero-trust architecture.", "All OEMs"],
    ["REQ-L4-037", "Detailed System Requirement (Security)", "The platform shall undergo automated container vulnerability scanning in the CI/CD pipeline before deployment.", "Test: Introduce a CVE into a Dockerfile; verify pipeline blocks deployment.", "System", "TC-040", "REQ-L3-037", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Security Module", "Shift-left security.", "All OEMs"],
    
    ["REQ-L3-039", "System Requirement", "The Global variant shall enforce data residency (EU in Frankfurt, US in Oregon).", "Inspection: Verify cloud DB region routing.", "System", "TC-041", "None", "Draft", "VAR-GLOB", "L3", "Cloud Key Service", "GDPR/CCPA compliance.", "All Global OEMs"],
    ["REQ-L3-040", "System Requirement", "The Global variant shall comply with CCPA by providing an 'Opt-Out of Sale of Personal Information' mechanism.", "Test: Verify user can toggle opt-out and data sharing ceases.", "System", "TC-042", "REQ-L3-039", "Draft", "VAR-GLOB", "L3", "Cloud Key Service", "California privacy law.", "OEM-US"],
    ["REQ-L5-038", "Software Requirement", "The system shall provide a 'Right to be Forgotten' API endpoint that permanently deletes all user PII within 30 days.", "Test: Call deletion API; verify DB records are purged.", "Integration", "TC-043", "REQ-L3-039", "Draft", "VAR-GLOB", "L5", "Cloud Key Service", "GDPR Art. 17.", "All Global OEMs"],
    ["REQ-L5-039", "Software Requirement", "The mobile app shall implement a granular consent management UI for data collection (analytics, location, push notifications).", "Test: Verify app respects user consent toggles in real-time.", "Integration", "TC-044", "REQ-L3-039", "Draft", "VAR-GLOB", "L5", "Mobile App", "ePrivacy Directive.", "All Global OEMs"],
    ["REQ-L5-040", "Software Requirement", "The system shall provide a 'Data Portability' API endpoint allowing users to export all their data in a machine-readable JSON format.", "Test: Call export API; verify JSON contains all user PII and activity logs.", "Integration", "TC-045", "REQ-L3-039", "Draft", "VAR-GLOB", "L5", "Cloud Key Service", "GDPR Art. 20.", "All Global OEMs"],

    # --- Performance & Scalability ---
    ["REQ-L4-038", "Detailed System Requirement (Performance)", "The API Gateway shall enforce rate limiting of 100 requests/minute per user to prevent abuse and DDoS.", "Test: Send 101 requests in 60s; verify 429 Too Many Requests response.", "System", "TC-046", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Cloud Key Service", "Standard API protection.", "All OEMs"],
    ["REQ-L4-039", "Detailed System Requirement (Scalability)", "The platform shall utilize read replicas for the primary database to offload read-heavy telemetry queries.", "Analysis: Review database architecture diagram for read replica configuration.", "System", "TC-047", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Cloud Key Service", "Database scaling strategy.", "All OEMs"],
    ["REQ-L5-041", "Software Requirement", "The platform shall serve all static mobile app assets (images, binaries) via a global Content Delivery Network (CDN).", "Test: Request asset from US and EU; verify response from nearest edge location.", "Integration", "TC-048", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Cloud Key Service", "Latency reduction.", "All OEMs"],

    # --- Reliability & Availability ---
    ["REQ-L4-040", "Detailed System Requirement (Reliability)", "Core platform services (Auth, Key Lifecycle) shall be deployed across multiple Availability Zones (Multi-AZ).", "Inspection: Review cloud infrastructure deployment topology.", "System", "TC-049", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Cloud Key Service", "High availability baseline.", "All OEMs"],
    ["REQ-L4-041", "Detailed System Requirement (Reliability)", "The platform shall perform automated daily backups of all databases with a Point-in-Time Recovery (PITR) window of 35 days.", "Test: Simulate data corruption; restore database to 1 hour prior.", "System", "TC-050", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Cloud Key Service", "Disaster recovery.", "All OEMs"],
    ["REQ-L3-041", "System Requirement", "The platform shall implement graceful degradation; if the Cloud Key Service is unreachable, the Mobile App shall cache the last known state and queue actions.", "Test: Block cloud access; verify app queues actions and syncs when restored.", "System", "TC-051", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Mobile App", "Offline-first UX.", "All OEMs"],

    # --- Observability & Monitoring ---
    ["REQ-L5-042", "Software Requirement", "The platform shall aggregate all application, security, and access logs into a centralized logging service.", "Test: Generate log in microservice A; verify it appears in centralized dashboard.", "Integration", "TC-052", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Cloud Key Service", "Centralized observability.", "All OEMs"],
    ["REQ-L4-042", "Detailed System Requirement (Observability)", "The platform shall trigger automated alerts (PagerDuty/Slack) when API error rates exceed 1% over a 5-minute window.", "Test: Inject 500 errors; verify alert is triggered within 5 minutes.", "System", "TC-053", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L4", "Cloud Key Service", "Proactive incident response.", "All OEMs"],
    ["REQ-L5-043", "Software Requirement", "The platform shall implement distributed tracing (OpenTelemetry) to track request flows across Mobile, API Gateway, and Microservices.", "Test: Generate request; verify trace ID is present in all downstream service logs.", "Integration", "TC-054", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Cloud Key Service", "Root cause analysis.", "All OEMs"],

    # --- Data Management ---
    ["REQ-L5-044", "Software Requirement", "The platform shall implement automated data lifecycle policies, moving telemetry older than 90 days to cold storage.", "Test: Insert record with timestamp > 90 days; verify it moves to cold storage.", "Integration", "TC-055", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L5", "Cloud Key Service", "Cost optimization.", "All OEMs"],

    # --- Global / Localization ---
    ["REQ-L3-042", "System Requirement", "The Global variant shall handle all time-based operations (rider profiles, logs) in UTC and convert to local timezone at the presentation layer.", "Test: Create time-window in Tokyo; verify it displays correctly in New York.", "System", "TC-056", "None", "Draft", "VAR-GLOB", "L3", "Cloud Key Service", "Timezone agnostic backend.", "All Global OEMs"],
    ["REQ-L5-045", "Software Requirement", "The platform shall enforce ISO 8601 standards for all date and time data exchanged via APIs.", "Test: Verify all API JSON responses use 'YYYY-MM-DDTHH:mm:ssZ' format.", "Integration", "TC-057", "REQ-L3-042", "Draft", "VAR-GLOB", "L5", "Cloud Key Service", "Standardized data exchange.", "All Global OEMs"],
    ["REQ-L5-046", "Software Requirement", "The mobile app shall support dynamic localization for 15 languages based on device OS settings.", "Test: Change device language to Japanese; verify app UI updates.", "Integration", "TC-058", "REQ-L3-042", "Draft", "VAR-GLOB", "L5", "Mobile App", "i18n resource bundles.", "All Global OEMs"],
    ["REQ-L3-043", "System Requirement", "The mobile application and web dashboards shall comply with WCAG 2.1 Level AA accessibility standards.", "Test: Run automated accessibility scanner (e.g., axe-core); verify zero critical violations.", "System", "TC-059", "None", "Draft", "VAR-BASE, VAR-PREM, VAR-FLEET", "L3", "Mobile App", "Inclusive design.", "All OEMs"]
]

# # ==========================================
# # 2. MASTER TEST CASES (V5 - ISO 29119 + Strict Traceability)
# # ==========================================
# test_cases_data = [
#     ["Test Plan ID", "Test Suite ID", "Test Case ID", "Linked Req IDs", "Test Type", "Test Objective", "Pre-conditions", "Test Steps (Summary)", "Expected Result", "Priority", "Status", "Owner", "Target Variant"],

#     # FEAT-01
#     ["STP-001", "TS-FEAT-01", "TC-ENR-001", "REQ-L2-001", "Functional", "Verify BLE pairing on Base.", "Vehicle BLE ON.", "1. Open App. 2. Scan.", "Pairing succeeds.", "High", "Pass", "QA-01", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-002", "REQ-L2-001", "Functional", "Verify UWB pairing on Premium.", "Vehicle UWB ON.", "1. Open App. 2. Scan.", "UWB pairing succeeds.", "High", "Pass", "QA-01", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-003", "REQ-L3-001", "Functional", "Verify end-to-end cloud provisioning.", "Cloud service running.", "1. Initiate enroll. 2. Check DB.", "Key record created.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-004", "REQ-L4-001", "Performance", "Measure enrollment latency.", "Network stable.", "1. Start timer. 2. Stop on success.", "Time < 15s.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-005", "REQ-L5-001", "Functional", "Verify Base BLE discovery.", "App installed.", "1. Scan for BLE.", "Vehicle appears.", "High", "Pass", "QA-01", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-006", "REQ-L5-002", "Security", "Verify Premium biometric block.", "Biometrics disabled.", "1. Attempt enroll.", "Blocked.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-007", "REQ-L5-003", "Functional", "Verify Fleet bulk CSV upload.", "10k CSV ready.", "1. Upload CSV.", "10k keys provisioned.", "High", "Pass", "QA-B2B", "VAR-FLEET"],
#     ["STP-001", "TS-FEAT-01", "TC-ENR-008", "REQ-L5-004", "Security", "Verify unauthenticated user blocked.", "User logged out.", "1. Attempt enroll.", "Prompt for login.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # FEAT-02
#     ["STP-001", "TS-FEAT-02", "TC-UNL-001", "REQ-L2-002", "Functional", "Verify Base passive unlock.", "Phone BLE ON.", "1. Approach vehicle.", "Unlocks.", "High", "Pass", "QA-01", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-002", "REQ-L2-002", "Functional", "Verify Premium UWB unlock.", "Phone UWB ON.", "1. Approach vehicle.", "Unlocks securely.", "High", "Pass", "QA-01", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-003", "REQ-L3-002", "Functional", "Verify proximity policy engine.", "Policy configured.", "1. Cross boundary.", "Action triggers.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-004", "REQ-L4-002", "Performance", "Measure Base BLE latency.", "Nominal conditions.", "1. Execute 50 times.", "p95 < 1.5s.", "Critical", "Fail", "QA-PERF", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-005", "REQ-L4-003", "Performance", "Measure Premium UWB latency.", "UWB active.", "1. Execute 50 times.", "p95 < 800ms.", "Critical", "Pass", "QA-PERF", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-006", "REQ-L5-005", "Functional", "Verify Base BLE RSSI unlock.", "Phone at -70 dBm.", "1. Move to -64 dBm.", "Unlocks.", "High", "Pass", "QA-02", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-007", "REQ-L5-006", "Security", "Verify Premium UWB relay attack prevention.", "Attacker has relay.", "1. Attempt relay.", "Fails. UWB unlocks.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-008", "REQ-L5-007", "Functional", "Verify Fleet remote API unlock.", "API creds valid.", "1. Send remote cmd.", "Unlocks remotely.", "High", "Pass", "QA-B2B", "VAR-FLEET"],
#     ["STP-001", "TS-FEAT-02", "TC-UNL-009", "REQ-L5-008", "Security", "Verify unknown key rejection.", "Unknown phone.", "1. Approach vehicle.", "Stays locked.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # FEAT-03
#     ["STP-001", "TS-FEAT-03", "TC-RID-001", "REQ-L2-003", "Functional", "Verify authorized ride start.", "Key valid.", "1. Tap Start.", "Ride starts.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-03", "TC-RID-002", "REQ-L3-003", "Security", "Verify valid key permits ride.", "Key valid.", "1. Tap Start.", "Permitted.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-03", "TC-RID-003", "REQ-L3-003", "Security", "Verify revoked key rejected.", "Key revoked.", "1. Tap Start.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-03", "TC-RID-004", "REQ-L4-003", "Performance", "Measure ignition latency.", "Network stable.", "1. Tap Start. 2. Measure relay.", "< 500ms.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-03", "TC-RID-005", "REQ-L5-009", "Functional", "Verify UI shows active status.", "Ride active.", "1. Check App.", "Shows 'Active'.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-03", "TC-RID-006", "REQ-L5-010", "Security", "Verify crypto handshake failure blocks ignition.", "Simulate timeout.", "1. Tap Start.", "Ignition disabled.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # FEAT-04
#     ["STP-001", "TS-FEAT-04", "TC-SHR-001", "REQ-L2-004", "Functional", "Verify owner can share key.", "Owner logged in.", "1. Create shared key.", "Key created.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-04", "TC-SHR-002", "REQ-L3-004", "Functional", "Verify shared key respects constraints.", "Constraint set.", "1. Use shared key.", "Constraint enforced.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-04", "TC-SHR-003", "REQ-L5-011", "Functional", "Verify Base time-expiry constraint.", "Expiry set to 1h.", "1. Wait 61 mins. 2. Use key.", "Fails.", "High", "Pass", "QA-01", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-04", "TC-SHR-004", "REQ-L5-012", "Security", "Verify Premium geo-fencing constraint.", "Geo-zone set.", "1. Use key outside zone.", "Fails.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-04", "TC-SHR-005", "REQ-L5-013", "Functional", "Verify shared keys list UI.", "2 keys active.", "1. Open list.", "Shows 2 keys.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # FEAT-05
#     ["STP-001", "TS-FEAT-05", "TC-REV-001", "REQ-L2-005", "Functional", "Verify owner can revoke key.", "Key active.", "1. Tap Revoke.", "Key revoked.", "Critical", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-05", "TC-REV-002", "REQ-L3-005", "Functional", "Verify revocation propagates.", "Vehicle online.", "1. Revoke. 2. Check vehicle.", "Vehicle rejects key.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-05", "TC-REV-003", "REQ-L4-005", "Performance", "Measure revocation propagation.", "Vehicle online.", "1. Revoke. 2. Measure time.", "< 10s.", "Critical", "Fail", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-05", "TC-REV-004", "REQ-L5-015", "Functional", "Verify Fleet bulk API revocation.", "1k keys active.", "1. Call bulk API.", "1k keys revoked.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

#     # FEAT-06
#     ["STP-001", "TS-FEAT-06", "TC-PRF-001", "REQ-L2-006", "Functional", "Verify Premium time-window UI.", "Premium app.", "1. Set time window.", "Saved.", "High", "Pass", "QA-01", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-06", "TC-PRF-002", "REQ-L3-006", "Security", "Verify policy engine denies outside window.", "Outside window.", "1. Attempt ride.", "Denied.", "Critical", "Pass", "QA-SEC", "VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-06", "TC-PRF-003", "REQ-L5-017", "Functional", "Verify Premium time-picker UI.", "Premium app.", "1. Set 09:00-17:00.", "Saved.", "Medium", "Pass", "QA-01", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-06", "TC-PRF-004", "REQ-L5-018", "Functional", "Verify Fleet shift-profile assignment.", "Fleet dashboard.", "1. Assign shift.", "Rider restricted to shift.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

#     # FEAT-07
#     ["STP-001", "TS-FEAT-07", "TC-VLT-001", "REQ-L2-007", "Functional", "Verify valet key creation.", "Owner logged in.", "1. Create valet key.", "Created.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-07", "TC-VLT-002", "REQ-L3-007", "Security", "Verify valet permissions masked.", "Valet key active.", "1. Attempt owner action.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-07", "TC-VLT-003", "REQ-L5-020", "Functional", "Verify Base valet speed limit.", "Valet key active.", "1. Accelerate.", "Capped at 20km/h.", "High", "Pass", "QA-02", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-07", "TC-VLT-004", "REQ-L5-021", "Functional", "Verify Premium valet trunk disable.", "Valet key active.", "1. Attempt trunk release.", "Disabled.", "High", "Pass", "QA-02", "VAR-PREM"],

#     # FEAT-08
#     ["STP-001", "TS-FEAT-08", "TC-SEC-001", "REQ-L2-008", "Functional", "Verify security event logging.", "Vehicle locked.", "1. Attempt unknown unlock.", "Event logged.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-08", "TC-SEC-002", "REQ-L3-008", "Security", "Verify unauthorized user cannot read logs.", "User B requests User A logs.", "1. Call API.", "403 Forbidden.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-08", "TC-SEC-003", "REQ-L3-008", "Functional", "Verify failed auth creates event.", "Unknown key.", "1. Attempt unlock 3x.", "3 events logged.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-08", "TC-SEC-004", "REQ-L4-007", "Compliance", "Verify Base 1-year retention.", "Base DB.", "1. Check policy.", "365 days.", "Medium", "Pass", "QA-COMP", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-08", "TC-SEC-005", "REQ-L4-008", "Compliance", "Verify Premium 5-year immutable retention.", "Premium Data Lake.", "1. Check policy.", "1825 days, WORM.", "Medium", "Pass", "QA-COMP", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-08", "TC-SEC-006", "REQ-L4-007-FLEET", "Functional", "Verify Fleet SIEM webhook.", "SIEM listener active.", "1. Trigger event.", "SIEM receives payload.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

#     # FEAT-09
#     ["STP-001", "TS-FEAT-09", "TC-STS-001", "REQ-L2-009", "Functional", "Verify status display.", "Vehicle locked.", "1. Open App.", "Shows locked.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-09", "TC-STS-002", "REQ-L3-009", "Functional", "Verify telemetry sync.", "Vehicle awake.", "1. Check App.", "Updates.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-09", "TC-STS-003", "REQ-L5-024", "Functional", "Verify Base REST polling.", "Vehicle locked.", "1. Pull to refresh.", "Updates within 60s.", "Medium", "Pass", "QA-01", "VAR-BASE"],
#     ["STP-001", "TS-FEAT-09", "TC-STS-004", "REQ-L5-025", "Performance", "Verify Premium WebSocket push.", "WebSocket active.", "1. Change lock state.", "Updates instantly.", "High", "Pass", "QA-PERF", "VAR-PREM"],
#     ["STP-001", "TS-FEAT-09", "TC-STS-005", "REQ-L5-026", "Performance", "Verify Fleet 10k WebSocket scale.", "10k simulated.", "1. Change 1k states.", "Updates within 5s.", "Critical", "Not Run", "QA-PERF", "VAR-FLEET"],

#     # FEAT-10
#     ["STP-001", "TS-FEAT-10", "TC-OFF-001", "REQ-L2-010", "Functional", "Verify offline grace permits ride.", "Offline 2h.", "1. Attempt ride.", "Permitted.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-10", "TC-OFF-002", "REQ-L3-010", "Security", "Verify offline grace rejects after expiry.", "Offline 73h.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-10", "TC-OFF-003", "REQ-L3-010", "Functional", "Verify local cache survives power cycle.", "Power cycle.", "1. Check cache.", "Persists.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-10", "TC-OFF-004", "REQ-L4-009", "Security", "Verify 72h hard limit.", "Offline 73h.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-001", "TS-FEAT-10", "TC-OFF-005", "REQ-L5-026", "Security", "Verify hard timeout logic.", "Timeout reached.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # ================= PLATFORM & GLOBAL TEST CASES (Clean IDs) =================
    
#     # --- Security & Compliance ---
#     ["STP-PLAT", "TS-PLAT-SEC", "TC-037", "REQ-L3-037", "Security", "Verify TLS 1.3 enforcement.", "Wireshark active.", "1. Capture API traffic.", "Handshake uses TLS 1.3.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-SEC", "TC-038", "REQ-L3-038", "Security", "Verify AES-256 encryption at rest.", "Database access.", "1. Inspect DB config.", "Encryption enabled.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-SEC", "TC-039", "REQ-L5-037", "Security", "Verify no hardcoded secrets.", "Source code access.", "1. Run secret scanning tool.", "Zero secrets found.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-SEC", "TC-040", "REQ-L4-037", "Security", "Verify CI/CD vulnerability scanning.", "CI/CD pipeline access.", "1. Push code with CVE.", "Pipeline fails.", "High", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    
#     ["STP-GLOB", "TS-GLOB-COMP", "TC-041", "REQ-L3-039", "Compliance", "Verify EU data residency.", "EU IP.", "1. Create user.", "Stored in Frankfurt.", "Critical", "Pass", "QA-COMP", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-COMP", "TC-042", "REQ-L3-040", "Compliance", "Verify CCPA opt-out mechanism.", "US User.", "1. Toggle opt-out.", "Data sharing stops.", "High", "Pass", "QA-COMP", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-COMP", "TC-043", "REQ-L5-038", "Compliance", "Verify Right to be Forgotten.", "User exists.", "1. Call DELETE API.", "PII purged.", "High", "Pass", "QA-COMP", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-COMP", "TC-044", "REQ-L5-039", "Compliance", "Verify granular consent UI.", "App installed.", "1. Toggle off analytics.", "Analytics stop.", "Medium", "Pass", "QA-COMP", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-COMP", "TC-045", "REQ-L5-040", "Compliance", "Verify Data Portability export.", "User has data.", "1. Call export API.", "JSON downloaded.", "Medium", "Pass", "QA-COMP", "VAR-GLOB"],

#     # --- Performance & Scalability ---
#     ["STP-PLAT", "TS-PLAT-PERF", "TC-046", "REQ-L4-038", "Performance", "Verify API rate limiting.", "API client.", "1. Send 101 reqs/min.", "429 response.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-PERF", "TC-047", "REQ-L4-039", "Performance", "Verify read replica offloading.", "DB access.", "1. Run heavy read query.", "Hits read replica.", "Medium", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-PERF", "TC-048", "REQ-L5-041", "Performance", "Verify CDN asset delivery.", "Global network.", "1. Request image from EU.", "Served from EU edge.", "Medium", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # --- Reliability & Availability ---
#     ["STP-PLAT", "TS-PLAT-REL", "TC-049", "REQ-L4-040", "Reliability", "Verify Multi-AZ deployment.", "Cloud console.", "1. Check deployment map.", "Spread across AZs.", "Critical", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-REL", "TC-050", "REQ-L4-041", "Reliability", "Verify Point-in-Time Recovery.", "DB backup enabled.", "1. Corrupt data. 2. Restore.", "Data restored.", "Critical", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-REL", "TC-051", "REQ-L3-041", "Reliability", "Verify graceful degradation offline.", "Block internet.", "1. Perform action.", "Action queued.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # --- Observability & Monitoring ---
#     ["STP-PLAT", "TS-PLAT-OBS", "TC-052", "REQ-L5-042", "Observability", "Verify centralized log aggregation.", "Logging dashboard.", "1. Generate log.", "Log appears.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-OBS", "TC-053", "REQ-L4-042", "Observability", "Verify automated error alerting.", "Alerting system.", "1. Inject 500 errors.", "Alert triggered.", "High", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
#     ["STP-PLAT", "TS-PLAT-OBS", "TC-054", "REQ-L5-043", "Observability", "Verify distributed tracing.", "Jaeger UI.", "1. Make API call.", "Trace ID visible.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # --- Data Management ---
#     ["STP-PLAT", "TS-PLAT-DATA", "TC-055", "REQ-L5-044", "Data", "Verify automated data lifecycle.", "Cold storage enabled.", "1. Insert old record.", "Moves to cold.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],

#     # --- Global / Localization ---
#     ["STP-GLOB", "TS-GLOB-LOC", "TC-056", "REQ-L3-042", "Functional", "Verify UTC backend / local frontend.", "Timezone settings.", "1. Set Tokyo time.", "Displays correctly.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-LOC", "TC-057", "REQ-L5-045", "Functional", "Verify ISO 8601 API dates.", "API client.", "1. Check JSON dates.", "Format correct.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
#     ["STP-GLOB", "TS-GLOB-LOC", "TC-058", "REQ-L5-046", "Functional", "Verify dynamic localization (Japanese).", "Device set to JP.", "1. Open App.", "UI in Japanese.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
#     ["STP-PLAT", "TS-PLAT-UX", "TC-059", "REQ-L3-043", "Usability", "Verify WCAG 2.1 AA compliance.", "Accessibility scanner.", "1. Run axe-core.", "Zero critical issues.", "High", "Pass", "QA-UX", "VAR-BASE, VAR-PREM, VAR-FLEET"]
# ]

# ==========================================
# 2. MASTER TEST CASES (V5 - ISO 29119 + Strict Traceability + Descriptions)
# ==========================================
test_cases_data = [
    # Headers (Added "Test Description" at index 3)
    ["Test Plan ID", "Test Suite ID", "Test Case ID", "Test Description", "Linked Req IDs", "Test Type", "Test Objective", "Pre-conditions", "Test Steps (Summary)", "Expected Result", "Priority", "Status", "Owner", "Target Variant"],

    # FEAT-01
    ["STP-001", "TS-FEAT-01", "TC-ENR-001", "Validates that a Base variant vehicle can be discovered via BLE and successfully initiates the enrollment sequence.", "REQ-L2-001", "Functional", "Verify BLE pairing on Base.", "Vehicle BLE ON.", "1. Open App. 2. Scan.", "Pairing succeeds.", "High", "Pass", "QA-01", "VAR-BASE"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-002", "Validates that a Premium variant vehicle utilizes UWB for secure discovery and enrollment initiation.", "REQ-L2-001", "Functional", "Verify UWB pairing on Premium.", "Vehicle UWB ON.", "1. Open App. 2. Scan.", "UWB pairing succeeds.", "High", "Pass", "QA-01", "VAR-PREM"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-003", "Validates the end-to-end flow of provisioning a digital key from the mobile app through the cloud to the vehicle controller.", "REQ-L3-001", "Functional", "Verify end-to-end cloud provisioning.", "Cloud service running.", "1. Initiate enroll. 2. Check DB.", "Key record created.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-004", "Measures the total time taken for the digital key enrollment process under nominal network conditions.", "REQ-L4-001", "Performance", "Measure enrollment latency.", "Network stable.", "1. Start timer. 2. Stop on success.", "Time < 15s.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-005", "Validates that the Base mobile app correctly discovers eligible vehicles using standard BLE protocols.", "REQ-L5-001", "Functional", "Verify Base BLE discovery.", "App installed.", "1. Scan for BLE.", "Vehicle appears.", "High", "Pass", "QA-01", "VAR-BASE"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-006", "Validates that the Premium app enforces on-device biometric authentication before allowing key provisioning.", "REQ-L5-002", "Security", "Verify Premium biometric block.", "Biometrics disabled.", "1. Attempt enroll.", "Blocked.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-007", "Validates the Fleet cloud service's ability to process bulk CSV uploads for mass key provisioning.", "REQ-L5-003", "Functional", "Verify Fleet bulk CSV upload.", "10k CSV ready.", "1. Upload CSV.", "10k keys provisioned.", "High", "Pass", "QA-B2B", "VAR-FLEET"],
    ["STP-001", "TS-FEAT-01", "TC-ENR-008", "Validates that unauthenticated users are blocked from initiating the digital key enrollment process.", "REQ-L5-004", "Security", "Verify unauthenticated user blocked.", "User logged out.", "1. Attempt enroll.", "Prompt for login.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # FEAT-02
    ["STP-001", "TS-FEAT-02", "TC-UNL-001", "Validates that a Base variant vehicle automatically unlocks when an authorized phone enters the BLE proximity zone.", "REQ-L2-002", "Functional", "Verify Base passive unlock.", "Phone BLE ON.", "1. Approach vehicle.", "Unlocks.", "High", "Pass", "QA-01", "VAR-BASE"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-002", "Validates that a Premium variant vehicle securely unlocks using UWB precise ranging.", "REQ-L2-002", "Functional", "Verify Premium UWB unlock.", "Phone UWB ON.", "1. Approach vehicle.", "Unlocks securely.", "High", "Pass", "QA-01", "VAR-PREM"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-003", "Validates the system's proximity policy engine correctly triggers actions when crossing defined boundaries.", "REQ-L3-002", "Functional", "Verify proximity policy engine.", "Policy configured.", "1. Cross boundary.", "Action triggers.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-004", "Measures the end-to-end unlock latency for the Base variant using BLE RSSI over 50 runs.", "REQ-L4-002", "Performance", "Measure Base BLE latency.", "Nominal conditions.", "1. Execute 50 times.", "p95 < 1.5s.", "Critical", "Fail", "QA-PERF", "VAR-BASE"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-005", "Measures the secure ranging handshake latency for the Premium variant using UWB over 50 runs.", "REQ-L4-003", "Performance", "Measure Premium UWB latency.", "UWB active.", "1. Execute 50 times.", "p95 < 800ms.", "Critical", "Pass", "QA-PERF", "VAR-PREM"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-006", "Validates that the Base vehicle controller unlocks specifically when BLE RSSI crosses the -64 dBm threshold.", "REQ-L5-005", "Functional", "Verify Base BLE RSSI unlock.", "Phone at -70 dBm.", "1. Move to -64 dBm.", "Unlocks.", "High", "Pass", "QA-02", "VAR-BASE"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-007", "Validates that the Premium UWB system successfully rejects a simulated BLE relay attack.", "REQ-L5-006", "Security", "Verify Premium UWB relay attack prevention.", "Attacker has relay.", "1. Attempt relay.", "Fails. UWB unlocks.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-008", "Validates that the Fleet vehicle controller accepts and executes remote unlock commands via the Fleet API.", "REQ-L5-007", "Functional", "Verify Fleet remote API unlock.", "API creds valid.", "1. Send remote cmd.", "Unlocks remotely.", "High", "Pass", "QA-B2B", "VAR-FLEET"],
    ["STP-001", "TS-FEAT-02", "TC-UNL-009", "Validates that the vehicle controller immediately rejects unlock requests from unrecognized digital key identifiers.", "REQ-L5-008", "Security", "Verify unknown key rejection.", "Unknown phone.", "1. Approach vehicle.", "Stays locked.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # FEAT-03
    ["STP-001", "TS-FEAT-03", "TC-RID-001", "Validates that an authorized rider with a valid key can successfully start the vehicle.", "REQ-L2-003", "Functional", "Verify authorized ride start.", "Key valid.", "1. Tap Start.", "Ride starts.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-03", "TC-RID-002", "Validates that the system permits ride authorization only when the cryptographic key is valid.", "REQ-L3-003", "Security", "Verify valid key permits ride.", "Key valid.", "1. Tap Start.", "Permitted.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-03", "TC-RID-003", "Validates that the system rejects ride authorization attempts using a revoked digital key.", "REQ-L3-003", "Security", "Verify revoked key rejected.", "Key revoked.", "1. Tap Start.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-03", "TC-RID-004", "Measures the latency between the mobile app 'Start' command and the physical ignition relay closure.", "REQ-L4-003", "Performance", "Measure ignition latency.", "Network stable.", "1. Tap Start. 2. Measure relay.", "< 500ms.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-03", "TC-RID-005", "Validates that the mobile app UI correctly displays the active ride authorization status to the rider.", "REQ-L5-009", "Functional", "Verify UI shows active status.", "Ride active.", "1. Check App.", "Shows 'Active'.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-03", "TC-RID-006", "Validates that the ignition remains disabled if the cryptographic challenge-response handshake fails or times out.", "REQ-L5-010", "Security", "Verify crypto handshake failure blocks ignition.", "Simulate timeout.", "1. Tap Start.", "Ignition disabled.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # FEAT-04
    ["STP-001", "TS-FEAT-04", "TC-SHR-001", "Validates that an authenticated vehicle owner can successfully create and distribute a shared digital key.", "REQ-L2-004", "Functional", "Verify owner can share key.", "Owner logged in.", "1. Create shared key.", "Key created.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-04", "TC-SHR-002", "Validates that a shared digital key strictly enforces the constraints (e.g., permissions) assigned by the owner.", "REQ-L3-004", "Functional", "Verify shared key respects constraints.", "Constraint set.", "1. Use shared key.", "Constraint enforced.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-04", "TC-SHR-003", "Validates that a Base variant shared key correctly expires and fails authentication after the configured time window.", "REQ-L5-011", "Functional", "Verify Base time-expiry constraint.", "Expiry set to 1h.", "1. Wait 61 mins. 2. Use key.", "Fails.", "High", "Pass", "QA-01", "VAR-BASE"],
    ["STP-001", "TS-FEAT-04", "TC-SHR-004", "Validates that a Premium variant shared key fails authentication if used outside the defined geofencing zone.", "REQ-L5-012", "Security", "Verify Premium geo-fencing constraint.", "Geo-zone set.", "1. Use key outside zone.", "Fails.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-001", "TS-FEAT-04", "TC-SHR-005", "Validates that the mobile app correctly renders a list of all active shared keys and their specific constraints.", "REQ-L5-013", "Functional", "Verify shared keys list UI.", "2 keys active.", "1. Open list.", "Shows 2 keys.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # FEAT-05
    ["STP-001", "TS-FEAT-05", "TC-REV-001", "Validates that an owner can successfully revoke an active shared digital key via the mobile app.", "REQ-L2-005", "Functional", "Verify owner can revoke key.", "Key active.", "1. Tap Revoke.", "Key revoked.", "Critical", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-05", "TC-REV-002", "Validates that a revocation command successfully propagates from the cloud to the vehicle controller.", "REQ-L3-005", "Functional", "Verify revocation propagates.", "Vehicle online.", "1. Revoke. 2. Check vehicle.", "Vehicle rejects key.", "Critical", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-05", "TC-REV-003", "Measures the time taken for a revocation command to propagate from the cloud to the vehicle controller.", "REQ-L4-005", "Performance", "Measure revocation propagation.", "Vehicle online.", "1. Revoke. 2. Measure time.", "< 10s.", "Critical", "Fail", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-05", "TC-REV-004", "Validates the Fleet API's ability to process bulk revocation requests for up to 1,000 keys simultaneously.", "REQ-L5-015", "Functional", "Verify Fleet bulk API revocation.", "1k keys active.", "1. Call bulk API.", "1k keys revoked.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

    # FEAT-06
    ["STP-001", "TS-FEAT-06", "TC-PRF-001", "Validates that the Premium mobile app allows an owner to configure and save a specific time-window restriction.", "REQ-L2-006", "Functional", "Verify Premium time-window UI.", "Premium app.", "1. Set time window.", "Saved.", "High", "Pass", "QA-01", "VAR-PREM"],
    ["STP-001", "TS-FEAT-06", "TC-PRF-002", "Validates that the cloud policy engine correctly denies ride authorization when attempted outside a configured time window.", "REQ-L3-006", "Security", "Verify policy engine denies outside window.", "Outside window.", "1. Attempt ride.", "Denied.", "Critical", "Pass", "QA-SEC", "VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-06", "TC-PRF-003", "Validates the functionality of the time-picker UI component within the Premium mobile application.", "REQ-L5-017", "Functional", "Verify Premium time-picker UI.", "Premium app.", "1. Set 09:00-17:00.", "Saved.", "Medium", "Pass", "QA-01", "VAR-PREM"],
    ["STP-001", "TS-FEAT-06", "TC-PRF-004", "Validates that the Fleet Dashboard correctly assigns shift-based profiles and restricts rider access accordingly.", "REQ-L5-018", "Functional", "Verify Fleet shift-profile assignment.", "Fleet dashboard.", "1. Assign shift.", "Rider restricted to shift.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

    # FEAT-07
    ["STP-001", "TS-FEAT-07", "TC-VLT-001", "Validates that an owner can successfully generate a temporary valet or service key.", "REQ-L2-007", "Functional", "Verify valet key creation.", "Owner logged in.", "1. Create valet key.", "Created.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-07", "TC-VLT-002", "Validates that a valet key correctly masks permissions, rejecting any owner-level actions.", "REQ-L3-007", "Security", "Verify valet permissions masked.", "Valet key active.", "1. Attempt owner action.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-07", "TC-VLT-003", "Validates that the Base vehicle controller enforces a 20km/h speed limit when a valet key is active.", "REQ-L5-020", "Functional", "Verify Base valet speed limit.", "Valet key active.", "1. Accelerate.", "Capped at 20km/h.", "High", "Pass", "QA-02", "VAR-BASE"],
    ["STP-001", "TS-FEAT-07", "TC-VLT-004", "Validates that the Premium vehicle controller disables the trunk release mechanism when a valet key is active.", "REQ-L5-021", "Functional", "Verify Premium valet trunk disable.", "Valet key active.", "1. Attempt trunk release.", "Disabled.", "High", "Pass", "QA-02", "VAR-PREM"],

    # FEAT-08
    ["STP-001", "TS-FEAT-08", "TC-SEC-001", "Validates that the system correctly logs a security event when an unknown key attempts to unlock the vehicle.", "REQ-L2-008", "Functional", "Verify security event logging.", "Vehicle locked.", "1. Attempt unknown unlock.", "Event logged.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-08", "TC-SEC-002", "Validates that unauthorized users receive a 403 Forbidden error when attempting to access security event logs.", "REQ-L3-008", "Security", "Verify unauthorized user cannot read logs.", "User B requests User A logs.", "1. Call API.", "403 Forbidden.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-08", "TC-SEC-003", "Validates that multiple failed authentication attempts generate distinct, timestamped log events.", "REQ-L3-008", "Functional", "Verify failed auth creates event.", "Unknown key.", "1. Attempt unlock 3x.", "3 events logged.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-08", "TC-SEC-004", "Validates that the Base variant cloud database enforces a 1-year retention policy for security logs.", "REQ-L4-007", "Compliance", "Verify Base 1-year retention.", "Base DB.", "1. Check policy.", "365 days.", "Medium", "Pass", "QA-COMP", "VAR-BASE"],
    ["STP-001", "TS-FEAT-08", "TC-SEC-005", "Validates that the Premium variant Data Lake enforces a 5-year immutable (WORM) retention policy.", "REQ-L4-008", "Compliance", "Verify Premium 5-year immutable retention.", "Premium Data Lake.", "1. Check policy.", "1825 days, WORM.", "Medium", "Pass", "QA-COMP", "VAR-PREM"],
    ["STP-001", "TS-FEAT-08", "TC-SEC-006", "Validates that the Fleet variant correctly streams security events to an external SIEM via webhook.", "REQ-L4-007-FLEET", "Functional", "Verify Fleet SIEM webhook.", "SIEM listener active.", "1. Trigger event.", "SIEM receives payload.", "High", "Pass", "QA-B2B", "VAR-FLEET"],

    # FEAT-09
    ["STP-001", "TS-FEAT-09", "TC-STS-001", "Validates that the mobile app correctly displays the current lock state of the vehicle.", "REQ-L2-009", "Functional", "Verify status display.", "Vehicle locked.", "1. Open App.", "Shows locked.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-09", "TC-STS-002", "Validates that the system successfully synchronizes telemetry data from the vehicle to the mobile app.", "REQ-L3-009", "Functional", "Verify telemetry sync.", "Vehicle awake.", "1. Check App.", "Updates.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-09", "TC-STS-003", "Validates that the Base app updates the lock state UI via standard REST polling within 60 seconds.", "REQ-L5-024", "Functional", "Verify Base REST polling.", "Vehicle locked.", "1. Pull to refresh.", "Updates within 60s.", "Medium", "Pass", "QA-01", "VAR-BASE"],
    ["STP-001", "TS-FEAT-09", "TC-STS-004", "Validates that the Premium app receives and displays real-time lock state updates via WebSockets.", "REQ-L5-025", "Performance", "Verify Premium WebSocket push.", "WebSocket active.", "1. Change lock state.", "Updates instantly.", "High", "Pass", "QA-PERF", "VAR-PREM"],
    ["STP-001", "TS-FEAT-09", "TC-STS-005", "Validates that the Fleet Dashboard can handle and render real-time telemetry updates for 10,000 simulated vehicles.", "REQ-L5-026", "Performance", "Verify Fleet 10k WebSocket scale.", "10k simulated.", "1. Change 1k states.", "Updates within 5s.", "Critical", "Not Run", "QA-PERF", "VAR-FLEET"],

    # FEAT-10
    ["STP-001", "TS-FEAT-10", "TC-OFF-001", "Validates that the vehicle permits ride authorization during the offline grace period.", "REQ-L2-010", "Functional", "Verify offline grace permits ride.", "Offline 2h.", "1. Attempt ride.", "Permitted.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-10", "TC-OFF-002", "Validates that the vehicle rejects ride authorization once the offline grace period has expired.", "REQ-L3-010", "Security", "Verify offline grace rejects after expiry.", "Offline 73h.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-10", "TC-OFF-003", "Validates that the vehicle's local authorization cache survives a complete power cycle.", "REQ-L3-010", "Functional", "Verify local cache survives power cycle.", "Power cycle.", "1. Check cache.", "Persists.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-10", "TC-OFF-004", "Validates the strict 72-hour hard limit for the offline grace mode.", "REQ-L4-009", "Security", "Verify 72h hard limit.", "Offline 73h.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-001", "TS-FEAT-10", "TC-OFF-005", "Validates the hard timeout logic that strictly terminates offline grace mode.", "REQ-L5-026", "Security", "Verify hard timeout logic.", "Timeout reached.", "1. Attempt ride.", "Rejected.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= PLATFORM & GLOBAL TEST CASES (Clean IDs) =================
    
    # --- Security & Compliance ---
    ["STP-PLAT", "TS-PLAT-SEC", "TC-037", "Validates that all API and cross-service communication strictly enforces TLS 1.3 encryption.", "REQ-L3-037", "Security", "Verify TLS 1.3 enforcement.", "Wireshark active.", "1. Capture API traffic.", "Handshake uses TLS 1.3.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-SEC", "TC-038", "Validates that sensitive data stored in databases and object storage is encrypted using AES-256.", "REQ-L3-038", "Security", "Verify AES-256 encryption at rest.", "Database access.", "1. Inspect DB config.", "Encryption enabled.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-SEC", "TC-039", "Validates that no hardcoded secrets exist in the source code or environment variables.", "REQ-L5-037", "Security", "Verify no hardcoded secrets.", "Source code access.", "1. Run secret scanning tool.", "Zero secrets found.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-SEC", "TC-040", "Validates that the CI/CD pipeline automatically blocks deployment if container vulnerabilities are detected.", "REQ-L4-037", "Security", "Verify CI/CD vulnerability scanning.", "CI/CD pipeline access.", "1. Push code with CVE.", "Pipeline fails.", "High", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    
    ["STP-GLOB", "TS-GLOB-COMP", "TC-041", "Validates that user data for EU residents is strictly routed and stored in the Frankfurt region.", "REQ-L3-039", "Compliance", "Verify EU data residency.", "EU IP.", "1. Create user.", "Stored in Frankfurt.", "Critical", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-COMP", "TC-042", "Validates that US users can successfully toggle the CCPA 'Opt-Out of Sale' mechanism.", "REQ-L3-040", "Compliance", "Verify CCPA opt-out mechanism.", "US User.", "1. Toggle opt-out.", "Data sharing stops.", "High", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-COMP", "TC-043", "Validates that the 'Right to be Forgotten' API permanently purges all user PII from the database.", "REQ-L5-038", "Compliance", "Verify Right to be Forgotten.", "User exists.", "1. Call DELETE API.", "PII purged.", "High", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-COMP", "TC-044", "Validates that the mobile app correctly respects user consent toggles for data collection in real-time.", "REQ-L5-039", "Compliance", "Verify granular consent UI.", "App installed.", "1. Toggle off analytics.", "Analytics stop.", "Medium", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-COMP", "TC-045", "Validates that the Data Portability API successfully exports all user data in a machine-readable JSON format.", "REQ-L5-040", "Compliance", "Verify Data Portability export.", "User has data.", "1. Call export API.", "JSON downloaded.", "Medium", "Pass", "QA-COMP", "VAR-GLOB"],

    # --- Performance & Scalability ---
    ["STP-PLAT", "TS-PLAT-PERF", "TC-046", "Validates that the API Gateway enforces a rate limit of 100 requests per minute per user.", "REQ-L4-038", "Performance", "Verify API rate limiting.", "API client.", "1. Send 101 reqs/min.", "429 response.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-PERF", "TC-047", "Validates that read-heavy telemetry queries are correctly offloaded to database read replicas.", "REQ-L4-039", "Performance", "Verify read replica offloading.", "DB access.", "1. Run heavy read query.", "Hits read replica.", "Medium", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-PERF", "TC-048", "Validates that static mobile app assets are served from the nearest global CDN edge location.", "REQ-L5-041", "Performance", "Verify CDN asset delivery.", "Global network.", "1. Request image from EU.", "Served from EU edge.", "Medium", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # --- Reliability & Availability ---
    ["STP-PLAT", "TS-PLAT-REL", "TC-049", "Validates that core platform services are deployed across multiple Availability Zones.", "REQ-L4-040", "Reliability", "Verify Multi-AZ deployment.", "Cloud console.", "1. Check deployment map.", "Spread across AZs.", "Critical", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-REL", "TC-050", "Validates that the database can be successfully restored to a specific point in time after simulated corruption.", "REQ-L4-041", "Reliability", "Verify Point-in-Time Recovery.", "DB backup enabled.", "1. Corrupt data. 2. Restore.", "Data restored.", "Critical", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-REL", "TC-051", "Validates that the mobile app gracefully degrades and queues actions when cloud connectivity is lost.", "REQ-L3-041", "Reliability", "Verify graceful degradation offline.", "Block internet.", "1. Perform action.", "Action queued.", "High", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # --- Observability & Monitoring ---
    ["STP-PLAT", "TS-PLAT-OBS", "TC-052", "Validates that application logs generated in microservices appear in the centralized logging dashboard.", "REQ-L5-042", "Observability", "Verify centralized log aggregation.", "Logging dashboard.", "1. Generate log.", "Log appears.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-OBS", "TC-053", "Validates that automated alerts are triggered when API error rates exceed the 1% threshold.", "REQ-L4-042", "Observability", "Verify automated error alerting.", "Alerting system.", "1. Inject 500 errors.", "Alert triggered.", "High", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT", "TS-PLAT-OBS", "TC-054", "Validates that distributed tracing correctly propagates trace IDs across all downstream services.", "REQ-L5-043", "Observability", "Verify distributed tracing.", "Jaeger UI.", "1. Make API call.", "Trace ID visible.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # --- Data Management ---
    ["STP-PLAT", "TS-PLAT-DATA", "TC-055", "Validates that telemetry records older than 90 days are automatically moved to cold storage.", "REQ-L5-044", "Data", "Verify automated data lifecycle.", "Cold storage enabled.", "1. Insert old record.", "Moves to cold.", "Medium", "Pass", "QA-OPS", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # --- Global / Localization ---
    ["STP-GLOB", "TS-GLOB-LOC", "TC-056", "Validates that time-based operations are stored in UTC and correctly converted to local timezones.", "REQ-L3-042", "Functional", "Verify UTC backend / local frontend.", "Timezone settings.", "1. Set Tokyo time.", "Displays correctly.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-LOC", "TC-057", "Validates that all API JSON responses strictly adhere to ISO 8601 date and time formatting.", "REQ-L5-045", "Functional", "Verify ISO 8601 API dates.", "API client.", "1. Check JSON dates.", "Format correct.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
    ["STP-GLOB", "TS-GLOB-LOC", "TC-058", "Validates that the mobile app UI dynamically updates to Japanese when the device OS language is changed.", "REQ-L5-046", "Functional", "Verify dynamic localization (Japanese).", "Device set to JP.", "1. Open App.", "UI in Japanese.", "Medium", "Pass", "QA-01", "VAR-GLOB"],
    ["STP-PLAT", "TS-PLAT-UX", "TC-059", "Validates that the mobile application and web dashboards meet WCAG 2.1 Level AA accessibility standards.", "REQ-L3-043", "Usability", "Verify WCAG 2.1 AA compliance.", "Accessibility scanner.", "1. Run axe-core.", "Zero critical issues.", "High", "Pass", "QA-UX", "VAR-BASE, VAR-PREM, VAR-FLEET"]
]

# ==========================================
# WRITE TO CSV FILES
# ==========================================
def write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(data)
    print(f"✅ Successfully generated {filename} with {len(data) - 1} rows!")

write_csv('data/requirements_master_v5.csv', requirements_data)
write_csv('data/test_cases_master_v5.csv', test_cases_data)