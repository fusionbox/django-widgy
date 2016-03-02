import unittest

from django.test import TestCase

from widgy.site import WidgySite
from widgy.models import Node
from widgy.exceptions import ParentChildRejection

from widgy.contrib.page_builder.models import (
    Table, TableRow, TableHeaderData, TableHeader, TableBody,
    Accordion, Video, MainContent
)
from widgy.contrib.page_builder.forms import CKEditorField


widgy_site = WidgySite()


def refetch(c):
    return Node.objects.get(pk=c.node.pk).content


class TestTableWidget(TestCase):
    def setUp(self):
        self.table = Table.add_root(widgy_site)

    def test_add_column(self):
        self.table.body.add_child(widgy_site, TableRow)
        self.table.body.add_child(widgy_site, TableRow)
        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 0)
        self.assertEqual(len(self.table.body.get_children()[1].get_children()), 0)

        self.table.header.add_child(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 1)
        self.assertEqual(len(self.table.body.get_children()[1].get_children()), 1)

    def test_add_column_front(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)
        row_2 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)

        cell_1 = row_1.get_children()[0]
        cell_2 = row_2.get_children()[0]

        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 2)
        self.assertEqual(len(self.table.body.get_children()[1].get_children()), 2)
        self.assertEqual(refetch(row_1).get_children()[1], cell_1)
        self.assertEqual(refetch(row_2).get_children()[1], cell_2)

    def test_three_columns(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        cell_1 = row_1.get_children()[0]
        cell_2 = row_1.get_children()[1]

        th3 = th1.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 3)
        self.assertEqual(refetch(row_1).get_children()[0], cell_1)
        self.assertEqual(refetch(row_1).get_children()[2], cell_2)

    def test_three_columns_front(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        cell_1 = row_1.get_children()[0]
        cell_2 = row_1.get_children()[1]

        th3 = th2.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 3)
        self.assertEqual(refetch(row_1).get_children()[1], cell_1)
        self.assertEqual(refetch(row_1).get_children()[2], cell_2)

    def test_add_row(self):
        self.table.header.add_child(widgy_site, TableHeaderData)
        self.table.header.add_child(widgy_site, TableHeaderData)
        self.table.body.add_child(widgy_site, TableRow)
        self.assertEqual(len(self.table.body.get_children()[0].get_children()), 2)

        self.table.body.add_child(widgy_site, TableRow)

        self.assertEqual(len(self.table.body.get_children()[1].get_children()), 2)

    def test_reorder(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        first_row_before = [i.pk for i in first_row.get_children()]
        second_row_before = [i.pk for i in second_row.get_children()]

        self.assertEqual(th1.get_next_sibling(), th2)

        th2.reposition(widgy_site, right=th1, parent=None)

        first_row, second_row = refetch(first_row), refetch(second_row)
        self.assertEqual(first_row_before, list(reversed([i.pk for i in first_row.get_children()])))
        self.assertEqual(second_row_before, list(reversed([i.pk for i in second_row.get_children()])))
        self.assertEqual(refetch(th2).get_next_sibling(), th1)
        self.assertEqual(refetch(th1).get_next_sibling(), None)

    def test_reorder_right_null(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        first_row_before = [i.pk for i in first_row.get_children()]
        second_row_before = [i.pk for i in second_row.get_children()]

        th1.reposition(widgy_site, right=None, parent=th1.get_parent())
        first_row, second_row = refetch(first_row), refetch(second_row)

        self.assertEqual(first_row_before, list(reversed([i.pk for i in first_row.get_children()])))
        self.assertEqual(second_row_before, list(reversed([i.pk for i in second_row.get_children()])))
        self.assertEqual(refetch(th1).get_next_sibling(), None)

    def test_delete_column(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        self.assertEqual(len(first_row.get_children()), 2)
        self.assertEqual(len(second_row.get_children()), 2)

        th1.delete()

        first_row, second_row = refetch(first_row), refetch(second_row)
        self.assertEqual(len(first_row.get_children()), 1)
        self.assertEqual(len(second_row.get_children()), 1)

    def test_compatibility(self):
        def invalid(parent, child_class):
            with self.assertRaises(ParentChildRejection):
                parent.add_child(widgy_site, child_class)

        # i don't know why these aren't raising
        # invalid(self.table, TableHeader)
        # invalid(self.table, TableBody)
        invalid(self.table.header, TableRow)
        invalid(self.table.body, TableHeaderData)

        row = self.table.body.add_child(widgy_site, TableRow)
        invalid(row, TableRow)
        invalid(row, TableHeaderData)

    def test_table_inside_of_table(self):
        # this mainly exercises TableElement.table
        self.table.header.add_child(widgy_site, TableHeaderData)
        tr = self.table.body.add_child(widgy_site, TableRow)
        td = tr.get_children()[0]
        table2 = td.add_child(widgy_site, Table)
        table2_tr = table2.body.add_child(widgy_site, TableRow)

        # the outer table has 1 column, the inside should have 0
        self.assertEqual(tr.get_children(), [td])
        self.assertEqual(table2_tr.get_children(), [])

    def test_move_rows(self):
        table1 = self.table
        table2 = Table.add_root(widgy_site)

        table1.header.add_child(widgy_site, TableHeaderData)
        table2.header.add_child(widgy_site, TableHeaderData)
        row = table2.body.add_child(widgy_site, TableRow)

        self.assertEqual(table2.body.get_children(), [row])
        self.assertEqual(table1.body.get_children(), [])
        # a row can be moved to another table with the same number of rows
        row.reposition(widgy_site, parent=table1.body)
        self.assertEqual(table1.body.get_children(), [row])
        self.assertEqual(table2.body.get_children(), [])

        # but not a table with a different number of rows
        table2.header.add_child(widgy_site, TableHeaderData)
        with self.assertRaises(ParentChildRejection):
            row.reposition(widgy_site, parent=table2.body)


class TestHtmlCleaning(TestCase):
    def test_it(self):
        """
        Make sure some common XSS vectors are filtered
        """

        test_cases = [
            ('<script>1', '<script>'),
            ('<a onclick="a">asdf</a>', 'onclick'),
            ("<IMG SRC=JaVaScRiPt:alert('XSS')>", 'XSS'),
            ('<div style="background: url("asdf");"></div>', 'url'),
            ('<a href="javascript:foo"></a>', 'javascript'),
            ('<link rel=stylesheet href=http://asdf>', '<link'),
            ('<meta HTTP-EQUIV="refresh" CONTENT="0;url=javascript:alert(1);">', '<meta'),
            ('<TABLE BACKGROUND="javascript:alert(1)">', 'javascript:'),
            (r"<DIV STYLE=\"background-image:\0075\0072\006C\0028'\006a\0061\0076\0061\0073\0063\0072\0069\0070\0074\003a\0061\006c\0065\0072\0074\0028.1027\0058.1053\0053\0027\0029'\0029\"></div>", 'background-image'),
            ('<p style="margin-left: expression(alert(1))">foo</p>', 'margin-left'),
            ('<HEAD><META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=UTF-7"> </HEAD>+ADw-SCRIPT+AD4-alert(1);+ADw-/SCRIPT+AD4-', '<meta'),
            ('<style>foo</style>', '<style'),
            ('<p style="-moz-binding: url("http://example.com")">asdf</p>', '-moz-binding'),
            ('<!--<script></script>-->', '<script>'),
            ('<img """><script>alert("xss")</script>">', '<script'),
            ('<img src= onmouseover="alert(1)">', ' onmouseover'),
            ('<html xmlns:xss><?import namespace="xss" implementation="http://ha.ckers.org/xss.htc"><xss:xss>ss</xss:xss></html>',
             '<?import'),
            ('<!--[if gte IE 4]><script>alert(1);</script><![endif]-->', '<script>'),
        ]

        for html, must_not_occur in test_cases:
            cleaned = CKEditorField().clean(html)
            self.assertNotIn(must_not_occur, cleaned)


class TestAccordionAutomaticallyAdds2Sections(TestCase):
    def test_adding_new_accordion_is_user_friendly(self):
        tabs = Accordion.add_root(widgy_site)
        self.assertEqual(len(tabs.get_children()), 2)
        self.assertEqual(tabs.get_children()[0].title, 'Title 1')
        self.assertEqual(tabs.get_children()[1].title, 'Title 2')


class TestVideoWidget(TestCase):
    def test_video_has_url(self):
        """Test video fetch from database."""

        content = MainContent.add_root(widgy_site)
        video = content.add_child(
            widgy_site,
            Video,
            video='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )

        video = content.get_children()[0]
        self.assertEqual(video.video.embed_url, '//youtube.com/embed/dQw4w9WgXcQ')
