"""Documents: upload, MIME allowlist, size limit, signed URLs, delete, and
cross-user isolation (metadata + private storage access)."""

PDF_BYTES = b"%PDF-1.4\n%fake minimal pdf content for testing\n"


def _upload(client, filename="transcript.pdf", content=PDF_BYTES, mime="application/pdf", document_type="Transcript"):
    return client.post(
        "/api/documents",
        files={"file": (filename, content, mime)},
        data={"document_type": document_type},
    )


def test_upload_accepted_mime_type_succeeds(user_a):
    client, _, _ = user_a
    response = _upload(client)
    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "transcript.pdf"
    assert body["mime_type"] == "application/pdf"
    assert body["document_type"] == "Transcript"


def test_upload_rejected_mime_type_is_blocked(user_a):
    client, _, _ = user_a
    response = _upload(client, filename="script.exe", content=b"MZ fake exe", mime="application/x-msdownload")
    assert response.status_code == 415


def test_upload_over_10mb_is_rejected(user_a):
    client, _, _ = user_a
    oversized = b"0" * (10 * 1024 * 1024 + 1)
    response = _upload(client, filename="huge.pdf", content=oversized)
    assert response.status_code == 413


def test_list_documents_after_upload(user_a):
    client, _, _ = user_a
    _upload(client)
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_download_returns_a_url_and_never_exposes_storage_credentials(user_a):
    client, _, _ = user_a
    document = _upload(client).json()

    response = client.get(f"/api/documents/{document['id']}/download")
    assert response.status_code == 200
    url = response.json()["url"]
    assert url.startswith("https://")
    # A signed URL must not leak our own service-role key or DB credentials.
    assert "service_role" not in url and "SUPABASE_SECRET_KEY" not in url


def test_delete_removes_document(user_a):
    client, _, _ = user_a
    document = _upload(client).json()

    response = client.delete(f"/api/documents/{document['id']}")
    assert response.status_code == 200

    listed = client.get("/api/documents").json()
    assert listed == []


def test_download_nonexistent_document_returns_404(user_a):
    client, _, _ = user_a
    response = client.get("/api/documents/00000000-0000-0000-0000-000000000000/download")
    assert response.status_code == 404


def test_documents_are_isolated_between_users(user_a, user_b):
    client_a, _, _ = user_a
    client_b, _, _ = user_b
    document_a = _upload(client_a).json()

    # B cannot list A's documents.
    listed_b = client_b.get("/api/documents").json()
    assert listed_b == []

    # B cannot get a signed download URL for A's document.
    download_by_b = client_b.get(f"/api/documents/{document_a['id']}/download")
    assert download_by_b.status_code == 404

    # B cannot delete A's document.
    delete_by_b = client_b.delete(f"/api/documents/{document_a['id']}")
    assert delete_by_b.status_code == 404

    # A's document is still there and still downloadable by A.
    still_there = client_a.get(f"/api/documents/{document_a['id']}/download")
    assert still_there.status_code == 200
