from django.test import TestCase
from django.utils import unittest

from widgy.site import WidgySite
from widgy.models import Node
from widgy.exceptions import ParentChildRejection

from widgy.contrib.page_builder.models import (Table, TableRow,
        TableHeaderData, TableHeader, TableBody)


widgy_site = WidgySite()


def refetch(c):
    return Node.objects.get(pk=c.node.pk).content


class TestTableWidget(TestCase):
    def setUp(self):
        self.table = Table.add_root(widgy_site)

    def test_add_column(self):
        self.table.body.add_child(widgy_site, TableRow)
        self.table.body.add_child(widgy_site, TableRow)
        self.assertEqual(len(self.table.body.children[0].children), 0)
        self.assertEqual(len(self.table.body.children[1].children), 0)

        self.table.header.add_child(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.children[0].children), 1)
        self.assertEqual(len(self.table.body.children[1].children), 1)

    def test_add_column_front(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)
        row_2 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)

        cell_1 = row_1.children[0]
        cell_2 = row_2.children[0]

        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.children[0].children), 2)
        self.assertEqual(len(self.table.body.children[1].children), 2)
        self.assertEqual(refetch(row_1).children[1], cell_1)
        self.assertEqual(refetch(row_2).children[1], cell_2)

    def test_three_columns(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        cell_1 = row_1.children[0]
        cell_2 = row_1.children[1]

        th3 = th1.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.children[0].children), 3)
        self.assertEqual(refetch(row_1).children[0], cell_1)
        self.assertEqual(refetch(row_1).children[2], cell_2)

    def test_three_columns_front(self):
        row_1 = self.table.body.add_child(widgy_site, TableRow)

        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = th1.add_sibling(widgy_site, TableHeaderData)

        cell_1 = row_1.children[0]
        cell_2 = row_1.children[1]

        th3 = th2.add_sibling(widgy_site, TableHeaderData)

        self.assertEqual(len(self.table.body.children[0].children), 3)
        self.assertEqual(refetch(row_1).children[1], cell_1)
        self.assertEqual(refetch(row_1).children[2], cell_2)

    def test_add_row(self):
        self.table.header.add_child(widgy_site, TableHeaderData)
        self.table.header.add_child(widgy_site, TableHeaderData)
        self.table.body.add_child(widgy_site, TableRow)
        self.assertEqual(len(self.table.body.children[0].children), 2)

        self.table.body.add_child(widgy_site, TableRow)

        self.assertEqual(len(self.table.body.children[1].children), 2)

    def test_reorder(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        first_row_before = [i.pk for i in first_row.children]
        second_row_before = [i.pk for i in second_row.children]

        self.assertEqual(th1.get_next_sibling(), th2)

        th2.reposition(widgy_site, right=th1, parent=None)

        first_row, second_row = refetch(first_row), refetch(second_row)
        self.assertEqual(first_row_before, list(reversed([i.pk for i in first_row.children])))
        self.assertEqual(second_row_before, list(reversed([i.pk for i in second_row.children])))
        self.assertEqual(refetch(th2).get_next_sibling(), th1)
        self.assertEqual(refetch(th1).get_next_sibling(), None)

    def test_reorder_right_null(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        first_row_before = [i.pk for i in first_row.children]
        second_row_before = [i.pk for i in second_row.children]

        th1.reposition(widgy_site, right=None, parent=th1.get_parent())
        first_row, second_row = refetch(first_row), refetch(second_row)

        self.assertEqual(first_row_before, list(reversed([i.pk for i in first_row.children])))
        self.assertEqual(second_row_before, list(reversed([i.pk for i in second_row.children])))
        self.assertEqual(refetch(th1).get_next_sibling(), None)

    def test_delete_column(self):
        th1 = self.table.header.add_child(widgy_site, TableHeaderData)
        th2 = self.table.header.add_child(widgy_site, TableHeaderData)
        first_row = self.table.body.add_child(widgy_site, TableRow)
        second_row = self.table.body.add_child(widgy_site, TableRow)

        self.assertEqual(len(first_row.children), 2)
        self.assertEqual(len(second_row.children), 2)

        th1.delete()

        first_row, second_row = refetch(first_row), refetch(second_row)
        self.assertEqual(len(first_row.children), 1)
        self.assertEqual(len(second_row.children), 1)

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
        td = tr.children[0]
        table2 = td.add_child(widgy_site, Table)
        table2_tr = table2.body.add_child(widgy_site, TableRow)

        # the outer table has 1 column, the inside should have 0
        self.assertEqual(tr.children, [td])
        self.assertEqual(table2_tr.children, [])
