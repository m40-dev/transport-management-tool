from PyQt6.QtCore import Qt
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
from lib.ui.CustomWidgets.TE_Table_TreeWidgetItem import TE_Table_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainer_TreeWidgetItem import TE_ObjectContainer_TreeWidgetItem

class TE_RelationColumn_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_RelationColumn_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(1, Qt.CheckState.Unchecked)
        self.setCheckState(2, Qt.CheckState.Unchecked)
        self.setCheckState(3, Qt.CheckState.Unchecked)
       
        if self.auto_select_default or isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
            self.update_relation_satus()
        
        if not self.auto_select_default and isinstance(source_widget, TemplateEditorListWidgetItem):
            self.set_relation_state(0)
        self.refresh()

    @property
    def auto_select_default(self):
        return self.application.ui.SelectWithDatabaseModelCheckBox.isChecked()

    @property
    def display_name(self):
        display = None

        if isinstance(self.object_data, dict):
            caption = self.get_table_display(self.ParentTable)
            display = f"{self.follow_column} - >> {self.ParentTable} ({caption})"
        
        if display is None:
            display = "Relation Column without display name"
        return display

    @property
    def follow_table(self):
        if self.TableGroup == self.ParentTable == self.source_widget.table_name:
            return self.ChildTable
        return self.ParentTable
    
    @property
    def follow_column(self):
        return self.ChildColumn

    @property
    def Relation(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("Relation", "0")

    @property
    def ChildTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildTable", "")

    @property
    def ChildColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildColumn", "")

    @property
    def ParentTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentTable", "")
            
    @property
    def ParentColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentColumn", "")
    
    @property
    def TableGroup(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("TableGroup", "")

    @property
    def InitialRelationState(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("InitialRelationState", 0)
        
    def set_relation_state(self, relation):
        self.object_data["Relation"] = relation

        if isinstance(self.source_widget, TemplateEditorTreeWidgetItem):
            self.source_widget.refresh()

        if isinstance(self.source_widget, TemplateEditorListWidgetItem):
            self.source_widget.set_relation_state(self.object_data)

        self.update_relation_satus()

    def show_relation(self, state):
        if self.InitialRelationState == 0:
            self.setHidden(not bool(state))

        parent_widget = self.parent()
        hide_parent = True
        if isinstance(parent_widget, TE_Table_TreeWidgetItem):
            for i in range(0, parent_widget.childCount()):
                if not parent_widget.child(i).isHidden():
                    hide_parent = False
                    break

        parent_widget.setHidden(hide_parent)
    
    def select_relations_using_db_model(self, state):
        if bool(state):
            self.set_relation_state(self.InitialRelationState)
        else:
            self.set_relation_state(0)

    def update_relation_satus(self):
        if self.Relation:
            if self.Relation in [1, 3, 5, 7]:
                self.setCheckState(1, Qt.CheckState.Checked)
            else:
                self.setCheckState(1, Qt.CheckState.Unchecked)
            
            if self.Relation in [2, 3, 7]:
                self.setCheckState(2, Qt.CheckState.Checked)
            else:
                self.setCheckState(2, Qt.CheckState.Unchecked)
            
            if self.Relation > 3:
                self.setCheckState(3, Qt.CheckState.Checked)
            else:
                self.setCheckState(3, Qt.CheckState.Unchecked)
        else:
            self.setCheckState(1, Qt.CheckState.Unchecked)
            self.setCheckState(2, Qt.CheckState.Unchecked)
            self.setCheckState(3, Qt.CheckState.Unchecked)
    
    def get_relation_state(self):
        relation = ""
        for i in reversed(range(1, 4)):
            relation += str(int(self.checkState(i) == Qt.CheckState.Checked))
        return self.binary2int(int(relation))

    def handle_data_change(self, column):
        status = self.get_relation_state()
        # print("relation change:", self.object_data, status)
        self.set_relation_state(status)
        tree_widget = self.treeWidget()
        column_state = self.checkState(column)
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_RelationColumn_TreeWidgetItem):
                element.setCheckState(column, column_state)
    
    def binary2int(self, binary): 
        int_val, i, n = 0, 0, 0
        while(binary != 0): 
            a = binary % 10
            int_val = int_val + a * pow(2, i) 
            binary = binary // 10
            i += 1
        return int_val

    def get_table_display(self, table_name):
        table_info = self.db.table_info.get(table_name, None)
        if table_info is not None:
            return table_info.DisplayName