# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestDocumentPage(common.TransactionCase):
    def setUp(self):
        super(TestDocumentPage, self).setUp()
        self.page_obj = self.env["document.page"]
        self.history_obj = self.env["document.page.history"]
        self.category1 = self.env.ref("document_page.demo_category1")
        self.page1 = self.env.ref("document_page.demo_page1")

    def test_page_creation(self):
        page = self.page_obj.create(
            {
                "name": "Test Page 1",
                "parent_id": self.category1.id,
                "content": "<p>Test content</p>",
            }
        )
        self.assertEqual(page.content, "<p>Test content</p>")
        self.assertEqual(len(page.history_ids), 1)
        page.content = "New content for Demo Page"
        self.assertEqual(len(page.history_ids), 2)
        page.content = "Another new content for Demo Page"
        self.assertEqual(len(page.history_ids), 3)
        # ensure history head is the latest revision (default sort order is ID DESC)
        self.assertEqual(page.history_head.id, max(page.history_ids.ids))

    def test_category_template(self):
        page = self.page_obj.create(
            {"name": "Test Page 2", "parent_id": self.category1.id}
        )
        page._onchange_parent_id()
        self.assertEqual(page.content, self.category1.template)

    def test_page_history_diff(self):
        page = self.page_obj.create(
            {"name": "Test Page 3", "content": "<p>Test content</p>"}
        )
        page.content = "New content"
        self.assertIsNotNone(page.history_ids[0].diff)

    def test_page_link(self):
        page = self.page_obj.create(
            {"name": "Test Page 3", "content": "<p>Test content</p>"}
        )
        self.assertEqual(
            page.backend_url,
            "/web#id={}&model=document.page&view_type=form".format(page.id),
        )
        menu = self.env.ref("knowledge.menu_document")
        page.menu_id = menu
        self.assertEqual(
            page.backend_url,
            "/web#id={}&model=document.page&view_type=form&action={}".format(
                page.id, menu.action.id
            ),
        )

    def test_page_copy(self):
        page = self.page_obj.create(
            {"name": "Test Page 3", "content": "<p>Test content</p>"}
        )
        page_copy = page.copy()
        self.assertEqual(page_copy.name, page.name + " (copy)")
        self.assertEqual(page_copy.content, page.content)
        self.assertEqual(page_copy.draft_name, "1.0")
        self.assertEqual(page_copy.draft_summary, "summary")
