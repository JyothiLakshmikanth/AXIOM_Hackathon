import csv

# ==========================================
# COMPREHENSIVE ISO 29119 TEST CASES (V4 - Massive Expansion)
# ==========================================
test_cases_data = [
    # Headers
    ["Test Plan ID", "Test Suite ID", "Test Case ID", "Linked Req IDs", "Test Type", "Test Objective", "Pre-conditions", "Test Steps (Summary)", "Expected Result", "Priority", "Status", "Owner", "Target Variant"],

    # ================= FEAT-01: Digital Key Enrollment =================
    ["STP-EKEY-001", "TS-FEAT-01-ENROLL", "TC-ENR-001", "REQ-BASE-L5-001", "Functional", "Verify BLE discovery on Base variant.", "Vehicle BLE ON. App installed.", "1. Open App. 2. Scan.", "Vehicle appears in list.", "High", "Pass", "QA-01", "VAR-BASE"],
    ["STP-EKEY-001", "TS-FEAT-01-ENROLL", "TC-ENR-002", "REQ-PLAT-L5-001", "Security", "Verify PII masking during enrollment logs.", "User email 'test@oem.com'.", "1. Enroll key. 2. Check logs.", "Email masked as '***@***.com'.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-01-ENROLL", "TC-ENR-003", "REQ-PREM-L3-001", "Security", "Verify biometric block on Premium.", "Biometrics disabled on phone.", "1. Attempt provisioning.", "App blocks and prompts for FaceID.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-01-ENROLL", "TC-ENR-004", "REQ-PLAT-L3-001", "Security", "Verify TLS 1.3 during key seed transfer.", "Wireshark running.", "1. Capture enrollment traffic.", "Handshake is TLS 1.3.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-01-ENROLL", "TC-ENR-005", "REQ-BASE-L4-001", "Performance", "Verify enrollment completes within 15s.", "Network latency < 50ms.", "1. Start timer on click. 2. Stop on success.", "Time < 15s.", "High", "Pass", "QA-PERF", "VAR-BASE"],

    # ================= FEAT-02: Passive Unlock/Lock =================
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-001", "REQ-L5-005-BASE", "Functional", "Verify Base BLE RSSI unlock.", "Phone at -70 dBm.", "1. Move phone to -64 dBm.", "Vehicle unlocks.", "High", "Pass", "QA-02", "VAR-BASE"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-002", "REQ-L5-005-PREM", "Security", "Verify Premium UWB prevents relay attack.", "Attacker has BLE relay.", "1. Attacker relays signal. 2. Owner approaches.", "Relay fails. UWB unlocks.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-003", "REQ-L5-005-FLEET", "Functional", "Verify Fleet remote unlock bypass.", "Fleet API credentials valid.", "1. Dispatcher sends unlock cmd.", "Vehicle unlocks remotely.", "High", "Pass", "QA-B2B", "VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-004", "REQ-L4-002", "Performance", "Measure Base unlock latency < 1.5s.", "Nominal conditions.", "1. Execute unlock 50 times.", "p95 < 1.5s.", "Critical", "Fail", "QA-PERF", "VAR-BASE, VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-005", "REQ-PREM-L4-001", "Performance", "Measure Premium UWB latency < 800ms.", "UWB hardware active.", "1. Execute UWB ranging 50 times.", "p95 < 800ms.", "Critical", "Pass", "QA-PERF", "VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-006", "REQ-L4-003", "Functional", "Verify hysteresis prevents flapping.", "Phone at -72 dBm (boundary).", "1. Hold position for 60s.", "No unlock/lock flapping.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-02-UNLOCK", "TC-UNL-007", "REQ-L5-007", "Security", "Verify unknown key rejection.", "Unknown phone approaches.", "1. Bring unknown phone to -60 dBm.", "Vehicle stays locked. Event logged.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-03: Ride Authorization =================
    ["STP-EKEY-001", "TS-FEAT-03-RIDE", "TC-RID-001", "REQ-L5-009", "Functional", "Verify UI shows active ride status.", "Key enrolled.", "1. Open App dashboard.", "Shows 'Ready to Ride'.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-03-RIDE", "TC-RID-002", "REQ-L5-010", "Security", "Verify crypto handshake failure blocks ignition.", "Simulate crypto timeout.", "1. Attempt 'Start Ride'.", "Ignition disabled. Error logged.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-03-RIDE", "TC-RID-003", "REQ-L5-011", "Security", "Verify cloud rejects revoked key for ride.", "Key revoked in DB.", "1. Attempt 'Start Ride'.", "Cloud returns 403. Ride blocked.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-03-RIDE", "TC-RID-004", "REQ-L4-004", "Performance", "Measure ignition signal latency < 500ms.", "Network stable.", "1. Tap 'Start'. 2. Measure relay click.", "Time < 500ms.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-04: Key Sharing =================
    ["STP-EKEY-001", "TS-FEAT-04-SHARE", "TC-SHR-001", "REQ-L5-012", "Security", "Verify shared key cannot exceed owner permissions.", "Shared key has 'No Trunk' restriction.", "1. Send trunk release cmd with shared key.", "Vehicle rejects command.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-04-SHARE", "TC-SHR-002", "REQ-L5-013", "Functional", "Verify owner sees active shared keys list.", "2 shared keys active.", "1. Open 'Shared Keys' menu.", "List shows 2 keys with constraints.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-04-SHARE", "TC-SHR-003", "REQ-L5-014", "Security", "Verify shared key stored in secure enclave.", "Rooted Android device.", "1. Attempt to extract key file.", "Extraction fails. Key encrypted.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-04-SHARE", "TC-SHR-004", "REQ-L4-005", "Performance", "Verify push notification delivery < 5s.", "Recipient app backgrounded.", "1. Owner shares key. 2. Measure receipt time.", "Time < 5s.", "High", "Pass", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-05: Key Revocation =================
    ["STP-EKEY-001", "TS-FEAT-05-REVOKE", "TC-REV-001", "REQ-L5-015", "Functional", "Verify Emergency Revoke All invalidates all keys.", "3 shared keys active.", "1. Tap 'Emergency Revoke All'.", "All 3 keys instantly invalidated.", "Critical", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-05-REVOKE", "TC-REV-002", "REQ-L5-016", "Functional", "Verify CRL sync every 60s.", "Vehicle online.", "1. Revoke key. 2. Monitor vehicle DB.", "Vehicle updates CRL within 60s.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-05-REVOKE", "TC-REV-003", "REQ-L4-006", "Performance", "Measure online revocation propagation < 10s.", "Vehicle online.", "1. Revoke key. 2. Attempt ride.", "Ride rejected within 10s.", "Critical", "Fail", "QA-PERF", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-06: Rider Profiles (Premium Only) =================
    ["STP-EKEY-001", "TS-FEAT-06-PROFILE", "TC-PRF-001", "REQ-L5-017", "Functional", "Verify owner can set time window.", "App logged in as owner.", "1. Set window 09:00-17:00. 2. Save.", "Saved and synced to cloud.", "High", "Pass", "QA-01", "VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-06-PROFILE", "TC-PRF-002", "REQ-L5-018", "Security", "Verify cloud rejects ride outside time window.", "Current time 18:00. Window 09-17.", "1. Rider attempts 'Start Ride'.", "Cloud returns 403.", "Critical", "Pass", "QA-SEC", "VAR-PREM"],
    ["STP-EKEY-001", "TS-FEAT-06-PROFILE", "TC-PRF-003", "REQ-L5-019", "Functional", "Verify vehicle enforces speed limit for restricted profile.", "Restricted key active.", "1. Accelerate vehicle.", "Speed capped at configured limit.", "High", "Pass", "QA-02", "VAR-PREM"],

    # ================= FEAT-07: Valet & Service Mode =================
    ["STP-EKEY-001", "TS-FEAT-07-VALET", "TC-VLT-001", "REQ-L5-020", "Functional", "Verify valet mode disables trunk and limits speed.", "Service key active.", "1. Attempt trunk release. 2. Accelerate.", "Trunk disabled. Speed limited to 20km/h.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-07-VALET", "TC-VLT-002", "REQ-L5-021", "Functional", "Verify service key auto-invalidates on expiry.", "Key expires in 1 hour.", "1. Wait 61 mins. 2. Attempt unlock.", "Unlock fails. Owner notified.", "Medium", "Pass", "QA-01", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-08: Security & Event Monitoring =================
    ["STP-EKEY-001", "TS-FEAT-08-SEC", "TC-SEC-001", "REQ-L5-022", "Functional", "Verify failed auth creates high-res log event.", "Vehicle locked.", "1. Attempt unlock with unknown key 3x.", "3 events logged with timestamps.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-08-SEC", "TC-SEC-002", "REQ-L3-008", "Security", "Verify unauthorized user cannot read logs.", "User B requests User A's logs.", "1. User B calls API.", "API returns 403 Forbidden.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-08-SEC", "TC-SEC-003", "REQ-L4-007", "Compliance", "Verify Base variant log retention is 1 year.", "Base variant DB.", "1. Check retention policy.", "Policy set to 365 days.", "Medium", "Pass", "QA-COMP", "VAR-BASE"],
    ["STP-EKEY-001", "TS-FEAT-08-SEC", "TC-SEC-004", "REQ-PREM-L4-002", "Compliance", "Verify Premium variant telemetry retention is 5 years.", "Premium variant Data Lake.", "1. Check retention policy.", "Policy set to 1825 days.", "Medium", "Pass", "QA-COMP", "VAR-PREM"],

    # ================= FEAT-09: Vehicle Status =================
    ["STP-EKEY-001", "TS-FEAT-09-STATUS", "TC-STS-001", "REQ-L5-024-BASE", "Functional", "Verify Base app polling shows lock state.", "Vehicle locked.", "1. Pull to refresh.", "Lock icon updates within 60s.", "Medium", "Pass", "QA-01", "VAR-BASE"],
    ["STP-EKEY-001", "TS-FEAT-09-STATUS", "TC-STS-002", "REQ-L5-024-FLEET", "Performance", "Verify Fleet WebSocket updates 10k vehicles.", "10k vehicles simulated.", "1. Change lock state on 1k vehicles.", "Dashboard updates within 5s.", "Critical", "Not Run", "QA-PERF", "VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-09-STATUS", "TC-STS-003", "REQ-L5-025", "Functional", "Verify vehicle sends MQTT telemetry every 60s.", "Vehicle awake.", "1. Monitor MQTT topic.", "Payload received every 60s.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= FEAT-10: Offline Grace Mode =================
    ["STP-EKEY-001", "TS-FEAT-10-OFFLINE", "TC-OFF-001", "REQ-L3-010", "Functional", "Verify offline grace permits ride.", "Offline 2 hours. Grace 72h.", "1. Attempt 'Start Ride'.", "Ride authorized.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-10-OFFLINE", "TC-OFF-002", "REQ-L5-026", "Security", "Verify expired grace rejects ride.", "Offline 73 hours.", "1. Attempt 'Start Ride'.", "Ride rejected. 'Connect to Cloud' shown.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-EKEY-001", "TS-FEAT-10-OFFLINE", "TC-OFF-003", "REQ-L5-027", "Functional", "Verify local cache survives power cycle.", "Vehicle powered off then on.", "1. Check local cache timestamp.", "Cache persists and is valid.", "High", "Pass", "QA-02", "VAR-BASE, VAR-PREM, VAR-FLEET"],

    # ================= PLATFORM & CROSS-CUTTING =================
    ["STP-PLAT-001", "TS-PLAT-SEC", "TC-PLT-001", "REQ-PLAT-L3-001", "Security", "Verify TLS 1.3 enforcement.", "Wireshark attached.", "1. Capture API call.", "TLS 1.3 used.", "Critical", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT-001", "TS-PLAT-SEC", "TC-PLT-002", "REQ-PLAT-L5-001", "Security", "Verify PII masking in logs.", "User email 'test@oem.com'.", "1. Trigger error.", "Log shows '***@***.com'.", "High", "Pass", "QA-SEC", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT-001", "TS-PLAT-OBS", "TC-PLT-003", "REQ-PLAT-L5-002", "Functional", "Verify OpenTelemetry trace propagation.", "Jaeger UI open.", "1. Make API request.", "Trace ID visible across services.", "Medium", "Pass", "QA-03", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    ["STP-PLAT-001", "TS-PLAT-REL", "TC-PLT-004", "REQ-L4-010", "Safety", "Verify OTA rollback on boot failure.", "Inject boot failure in new FW.", "1. Flash new FW. 2. Reboot.", "Auto-rollback to previous FW.", "Critical", "Pass", "QA-SAF", "VAR-BASE, VAR-PREM, VAR-FLEET"],
    
    # ================= GLOBAL / COMPLIANCE =================
    ["STP-GLOB-001", "TS-GLOB-COMP", "TC-GLB-001", "REQ-GLOB-L3-001", "Compliance", "Verify EU data residency in Frankfurt.", "User registered with EU IP.", "1. Create user. 2. Check DB.", "Data in eu-central-1.", "Critical", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB-001", "TS-GLOB-COMP", "TC-GLB-002", "REQ-GLOB-L5-001", "Compliance", "Verify Right to be Forgotten API.", "User has active data.", "1. Call DELETE API.", "PII purged.", "High", "Pass", "QA-COMP", "VAR-GLOB"],
    ["STP-GLOB-001", "TS-GLOB-LOC", "TC-GLB-003", "REQ-GLOB-L5-002", "Functional", "Verify dynamic localization (Japanese).", "Device language set to Japanese.", "1. Open App.", "UI renders in Japanese.", "Medium", "Pass", "QA-01", "VAR-GLOB"]
]

# ==========================================
# WRITE TO CSV FILE
# ==========================================
def write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(data)
    print(f"✅ Successfully generated {filename} with {len(data) - 1} test cases!")

write_csv('data/test_cases_massive_v4.csv', test_cases_data)