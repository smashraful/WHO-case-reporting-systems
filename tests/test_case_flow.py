from app.models.enums import UserRole


def _create_patient(client, auth_headers):
    resp = client.post(
        "/patients",
        json={"full_name": "Child A", "sex": "male", "vaccination_status": "unvaccinated"},
        headers=auth_headers(UserRole.field_worker),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_patient_create_requires_field_worker(client, auth_headers):
    # lab_staff may not register patients
    resp = client.post(
        "/patients",
        json={"full_name": "X"},
        headers=auth_headers(UserRole.lab_staff),
    )
    assert resp.status_code == 403


def test_full_case_flow_and_event_emission(client, auth_headers, mock_infra):
    patient_id = _create_patient(client, auth_headers)

    # field_worker files a case
    resp = client.post(
        "/cases",
        json={"patient_id": patient_id, "report_date": "2026-08-01", "has_rash": True},
        headers=auth_headers(UserRole.field_worker),
    )
    assert resp.status_code == 201, resp.text
    case = resp.json()
    case_id = case["id"]
    assert case["status"] == "suspected"

    # case.created event was published
    assert mock_infra["published"].called
    assert mock_infra["published"].call_args.args[0] == "case.created"

    # lab_staff attaches a result
    resp = client.post(
        f"/cases/{case_id}/lab-results",
        json={"specimen_type": "serum", "result": "igm_positive"},
        headers=auth_headers(UserRole.lab_staff),
    )
    assert resp.status_code == 201, resp.text

    # field_worker cannot verify
    resp = client.patch(
        f"/cases/{case_id}/status",
        json={"status": "confirmed"},
        headers=auth_headers(UserRole.field_worker),
    )
    assert resp.status_code == 403

    # district_officer confirms the case
    resp = client.patch(
        f"/cases/{case_id}/status",
        json={"status": "confirmed"},
        headers=auth_headers(UserRole.district_officer),
    )
    assert resp.status_code == 200, resp.text
    confirmed = resp.json()
    assert confirmed["status"] == "confirmed"
    assert confirmed["verified_by"] is not None

    # case.confirmed event emitted
    assert mock_infra["published"].call_args.args[0] == "case.confirmed"


def test_case_stats_requires_privileged_role(client, auth_headers):
    # field_worker cannot see aggregate stats
    resp = client.get("/cases/stats", headers=auth_headers(UserRole.field_worker))
    assert resp.status_code == 403

    resp = client.get("/cases/stats", headers=auth_headers(UserRole.program_manager))
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"total", "by_status", "by_location"}


def test_create_case_for_missing_patient_returns_404(client, auth_headers):
    resp = client.post(
        "/cases",
        json={"patient_id": 9999, "report_date": "2026-08-01"},
        headers=auth_headers(UserRole.field_worker),
    )
    assert resp.status_code == 404
