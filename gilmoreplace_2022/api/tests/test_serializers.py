from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from gilmoreplace_2022.api.serializers import (
    _resolve_about_collage,
    _resolve_link_block,
    _resolve_paragraph,
    _resolve_related_links,
    resolve_streamfield_blocks,
)


class ResolveRelatedLinksTests(SimpleTestCase):
    def test_email_link_is_preserved(self):
        links = {
            "align": "text-center",
            "links": [
                {
                    "type": "email_link",
                    "value": {
                        "title": "Contact Us",
                        "link_type": "reverse",
                        "link": "leasing@onni.com",
                    },
                }
            ],
        }

        resolved = _resolve_related_links(links)

        self.assertEqual(resolved["links"][0]["type"], "email_link")
        self.assertEqual(resolved["links"][0]["value"]["link"], "leasing@onni.com")


class ResolveParagraphTests(TestCase):
    @patch("gilmoreplace_2022.api.serializers.resolve_theme")
    def test_resolves_theme_and_links(self, resolve_theme):
        resolve_theme.return_value = {"id": 3, "css_class": "about-onni-theme"}

        resolved = _resolve_paragraph(
            {
                "title": "MORE",
                "theme": 3,
                "new_links": {
                    "links": [
                        {
                            "type": "onni_link",
                            "value": {"title": "ONNI", "new_window": True},
                        }
                    ]
                },
            }
        )

        self.assertEqual(resolved["theme"]["css_class"], "about-onni-theme")
        self.assertEqual(resolved["new_links"]["links"][0]["type"], "onni_link")
        resolve_theme.assert_called_once_with(3)


class ResolveAboutCollageTests(TestCase):
    @patch("gilmoreplace_2022.api.serializers.resolve_image")
    def test_resolves_image_groups(self, resolve_image):
        resolve_image.return_value = {
            "id": 310,
            "url": "/media_files/images/building.jpg",
            "alt": "building",
        }

        resolved = _resolve_about_collage(
            {
                "title": "Visit Onni",
                "image_groups": [
                    {
                        "images": [
                            {"title": "CentreView", "image": 310},
                        ]
                    }
                ],
            }
        )

        groups = resolved["resolved_image_groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["resolved_images"][0]["title"], "CentreView")
        self.assertEqual(
            groups[0]["resolved_images"][0]["resolved_image"]["url"],
            "/media_files/images/building.jpg",
        )
        resolve_image.assert_called_once_with(310, "max-640x640")


class ResolveStreamFieldBlocksTests(SimpleTestCase):
    def test_resolves_info_and_paragraph_blocks(self):
        raw = [
            {
                "type": "paragraph",
                "id": "p1",
                "value": {"title": "Hello", "text": "<p>Body</p>"},
            },
            {
                "type": "info",
                "id": "i1",
                "value": {
                    "title": "Stat",
                    "items": [{"title": "One", "text": "<p>Item</p>"}],
                },
            },
        ]

        with patch("gilmoreplace_2022.api.serializers._resolve_paragraph") as paragraph:
            paragraph.side_effect = lambda value: {**value, "resolved": True}
            blocks = resolve_streamfield_blocks(raw)

        self.assertEqual(blocks[0]["type"], "paragraph")
        self.assertTrue(blocks[0]["value"]["resolved"])
        self.assertEqual(blocks[1]["type"], "info")
        self.assertEqual(blocks[1]["value"]["items"][0]["title"], "One")


class ResolveLinkBlockTests(SimpleTestCase):
    def test_internal_page_link_resolves_page(self):
        with patch("gilmoreplace_2022.api.serializers.resolve_page") as resolve_page:
            resolve_page.return_value = {"url": "/en/contact/"}
            resolved = _resolve_link_block("internal_page_link", {"link": 99})

        self.assertEqual(resolved["value"]["resolved_link"]["url"], "/en/contact/")
