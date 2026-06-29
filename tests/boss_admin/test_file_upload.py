"""Tests for boss_admin/file_upload/fileUpload.py."""
from unittest.mock import MagicMock, patch

import pytest

from boss_admin.file_upload.fileUpload import file_upload


class TestInsertDocuments:
    def test_skips_when_document_id_set(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            files = [
                {
                    "file_name": "a.png",
                    "file_type": "png",
                    "section": "S1",
                    "document_id": "existing",
                    "file": "data",
                }
            ]
            resp = file_upload.insert_documents("PSC", "app", "REV1", files, "u")
        Doc.objects.create.assert_not_called()
        assert resp.content == b"Success"

    def test_creates_new_document_when_no_document_id(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            files = [
                {
                    "file_name": "a.png",
                    "file_type": "png",
                    "section": "S1",
                    "document_id": "",
                    "file": "data",
                }
            ]
            resp = file_upload.insert_documents("PSC", "app", "REV1", files, "u")
        Doc.objects.create.assert_called_once()
        kwargs = Doc.objects.create.call_args.kwargs
        assert kwargs["file_name"] == "a.png"
        assert kwargs["review_type"] == "PSC"
        assert kwargs["review_id"] == "REV1"
        assert kwargs["app"] == "app"
        assert kwargs["created_user"] == "u"
        assert resp.content == b"Success"

    def test_returns_failure_on_exception(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            Doc.objects.create.side_effect = RuntimeError("db down")
            files = [
                {
                    "file_name": "a.png",
                    "file_type": "png",
                    "section": "S",
                    "document_id": "",
                    "file": "data",
                }
            ]
            resp = file_upload.insert_documents("PSC", "app", "REV", files, "u")
        assert resp.content == b"Failed"

    def test_empty_files_list_returns_success(self):
        resp = file_upload.insert_documents("PSC", "app", "REV", [], "u")
        assert resp.content == b"Success"


class TestGetAllDocuments:
    def test_filters_by_review_and_app(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            Doc.objects.filter.return_value.values.return_value = [{"id": 1}]
            result = file_upload.get_all_documents("psc", "REV1")
        Doc.objects.filter.assert_called_with(review_id="REV1", app="psc")
        assert result == [{"id": 1}]


class TestGetSingleDocument:
    def test_filters_by_document_id(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            Doc.objects.filter.return_value.values.return_value = [{"file": "x"}]
            result = file_upload.get_single_document(7)
        Doc.objects.filter.assert_called_with(document_id=7)
        assert result == [{"file": "x"}]


class TestDeleteDocuments:
    def test_deletes_and_returns_success(self):
        with patch(
            "boss_admin.file_upload.fileUpload.DocumentTable"
        ) as Doc:
            qs = MagicMock()
            Doc.objects.filter.return_value = qs
            resp = file_upload.delete_documents(1)
        qs.delete.assert_called_once()
        assert resp.content == b"Success"
