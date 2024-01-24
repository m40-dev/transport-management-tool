XML Template editor is a view where the xml template definition for the transport package can be organized and prepared for the database transporter tool.

The main view is organized in following sections:

1. **Side Bar** - navigation between views - Package Manager, XML Template Editor and Application Settings 
2. **Database Objects query section** - search for database objects to be included in the transport template
3. **Search results and object configuration view** - shows the list of database objects returned from the object query section and is used to configure the object relations or database object listing parameters in the xml structure. these views dynamically switch when relevant object is clicked on the XML Structure Treeview
4. **XML Structure Tree View** - main view where the transport template structure is built and organized
5. **XML Output File Preview** - shows final xml template structure based on the xml structure tree view
6. Information about currently connected session
7. Connections menu where the target database for object queries can be selected

![](screenshots/Pasted%20image%2020240124184254.png)

# XML Template Editor Actions

The XML Template Editor view provides a set of minimum actions which should effectively help with the overall structure of the xml template.
It is possible to work "offline" on the templates, however major functionality requires the database connection to load the objects and table relations information. 

## Create new transport template

You can open xml template using the dedicated **menu** action.
New template is opened in new tab and will have the initial xml structure generated (up to **tasks** structure).

## Load existing XML template

You can open xml template using the dedicated **menu** action or from the [Package Manager](Package%20Manager.md) object definitions view integration.
If the file is not recognized, it will be used as target file but empty transport template will be created.

When loading the transport template where object transport tasks with relation configurations are defined, each object container is parsed and can be configured in scope of this xml definition only.

**Note:** Currently only Database Object Transport and SQL Script transport tasks can be fully managed with the xml template editor. Any other task can be only parsed, moved around and deleted.

## Edit XML Template structure

You can edit xml template structure by simple **drag and drop** operations - these changes can be done on single items or on multi-selected objects.
Application validates and prevents certain movement operations, but it is important that you verify and create correct object structures that can be then parsed by the database transporter tool. 

## Add XML structure nodes

Currently only Database Object Transport and SQL Script transport tasks can be fully managed with the xml template editor. Using the context menu you can create the object transport task or SQL Script task with their respective SQL script nodes.
New transport tasks can be also created by dropping the database object from the search results list, however this functionality requires database connection to operate. SQL Script tasks can be created and managed offline.

## Delete XML structure nodes

You can delete single or multi-selected xml structure nodes by simply pressing the delete key. Application will delete the entry from xml structure of currently active xml template editor.

## Load and list database objects automatically

This action requires database connection to work properly. If no active connection is established, you will get a popup to connect first and try again.
Each of these actions can be initiated from the context menu in the xml structure tree view and is only available for the objects which represent the transport object container.

Automatic listing allows for live preview of how the selected database relations affect the related objects that would be selected by the database transporter - this is only orientational information since in some edge cases this information might not be accurate enough. 

## Edit transport object relations

The Object relations view provides graphical representation of the xml object relations or available database object relations (updated when the database object is loaded). Relations view is updated when the active XML Transport Structure object is selected **(1)**.

![](screenshots/Pasted%20image%2020240124184716.png)


After the Object Transport Container is selected, the available relation presets are loaded **(2)** and also the current object relation configuration. The Object Configuration view is always automatically opened whenever the object container is selected from the XML Transport Structure view.

Relations can be edited with the checkboxes which are corresponding to the respective relation instructions:

**FK** - object referenced by the foreign key of the base object

**CR** - objects referencing the base object through child foreign key reference

**SH** - selects the 'Ignore in superset handling' flag

Object Relations view can be configured with additional options:

![](screenshots/Pasted%20image%2020240124184754.png)

**Auto List Selected Objects from database** - This option controls whether the database objects referenced via object relations will be automatically listed in the XML Structure View according to the currently active database connection. When this option is set, database objects will be automatically loaded where required. This is helpful to preview relation changes in the XML Structure editor, but can prolong the loading times of complex XML templates where all object transport containers will be loaded at the same time.

**Auto Load Matching Objects from database** - Will only attempt to identify and load the corresponding database object in the currently active connection.

**Show All Columns** - By default the relations view show only the selected relations or relations that have clear instructions in the database table relations data. If database model does not provide any instruction which relation option should be used by default, the relation will be hidden. 

**Deselect All Relations** - Clear any object relation settings for the selected object transport container.

**Reset To Initial State** - This action can reset the object relations to the state defined by the database model configuration.

### Follow table relations
In database relation editor only the close object relations are loaded to avoid loopback and can be extended manually if required.

If the object relation contains instruction for the target table where the object relation follows the relation, the table relation can be loaded using the context menu of the object relation entry:

![](screenshots/Pasted%20image%2020240124184830.png)

Once the action is performed, all of the target table relations are loaded and can be selected from the tree structure.

![](screenshots/Pasted%20image%2020240124184849.png)

Note: when the object container is re-loaded or relations are refreshed, any additional table relations will be loaded in the top-level structure. This sub-tree view is only generated when additional relations are loaded manually.

### Edit table relations

Whenever the relation configuration is changed, the XML file preview is refreshed to show the effective file structure, but also the related objects can be listed in the XML Transport Structure view if the auto listing option is enabled.

![](screenshots/Pasted%20image%2020240124184933.png)

On this example, the selected table relations would show that **1 AccProduct** and **1 AccProductGroup** will be selected in the transport. The treeview can be extended further to see which items are loaded, however only display names of the selected items are currently available.

![](screenshots/Pasted%20image%2020240124184953.png)

## Save Relation Preset

Transport containers in the Object Transport tasks have usually some sort of relation configured and it is possible to save those relations to be then transferred on different object types.
To save the relation configuration of a specific object transport container, right click the item on the **XML Structure Tree View**  and select the action from the context menu.

![](screenshots/Pasted%20image%2020240124185015.png)

## Apply Relation Preset

Saved relation presets are automatically loaded in the  **Object relations management view (2, 3)** when the object container is activated **(1)**.

![](screenshots/Pasted%20image%2020240124185125.png)

After the preset is selected from the drop-down list (2) it can be applied to the selected object container or containers(applies only to the objects of the same type) by pressing the apply button (3).

Only presets that are relevant for this object type are listed and can be applied.

When the preset is applied to the selected objects, the effective relations of the object container are updated and then the relations in view **3** will be **overwritten** according to the selected preset data.

## Edit SQL Scripts

SQL Script tasks can be directly edited from the XML Template Editor UI. 

![](screenshots/Pasted%20image%2020240124185241.png)

Simply select the Edit SQL Script from XML Tree View item context menu and the editor will show up.

![](screenshots/Pasted%20image%2020240124185310.png)

Once the SQL Script content is accepted, tool will parse it and save it in the right format into the XML structure (mostly the encoding and XObjectKey escaping is done for the database transporter to read and use these scripts correctly). 

## Bulk change the Transport task options 

Transport tasks or task containers have their specific options to be configured - these object specific flags are displayed in the "Options" column where the option respective to the task can be toggled.

In the following example all of the object transport tasks can be configured with the "Delete Residual Items" parameter at once:

![](screenshots/Pasted%20image%2020240124185503.png)

In both cases the flags can be applied to single items or in bulk to all selected rows of the same type in the XML Structure Tree View. 
This means that if Object Transport Task option was toggled, it will be only reflected to other Object Transport tasks only, ignoring other object classes.

## Query this table

This option from the context menu allows for quick switch of the table filter to search for objects from the table in which the object resides or where the data for the transport task is expected.

![](screenshots/Pasted%20image%2020240124185851.png)

In the above example the object container for **AccProduct** table was clicked, so the **AccProduct** table would be applied in the filter and objects would be listed from there.

Some table queries are fixed depending on the transport task types:
* Change Label -> DialogTag
* Synchronization Project -> DPRShell
* File Transport -> QBMFileRevision

If the selected object does not have a corresponding table name information, the context menu option will not be available.

