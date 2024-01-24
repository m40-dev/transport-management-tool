Package manager is the view where all transport packages and their dependencies can be organized.

The main view is organized in following sections:

1. **Side Bar** - navigation between views - Package Manager, XML Template Editor and Application Settings 
2. **Package definitions view** - preview of all of your defined packages (effectively JSON defined objects)
3. **Execution planner view** - side view for execution planner operations, queue tasks to be executed here. More detailed description of the execution planner can be found in the dedicated page: [[Execution Planner]]
4. **Execution planner output console** - console shows the process runner commands but also the output from the tools/commands which are actually running the task. 
	Initially this console is hidden and shows up when first task is executed.

![](screenshots/Pasted%20image%2020240124181754.png)

# Package Definitions view

Package definition view breaks down into following components:

1. Search Filter - allows filtering of the transport definitions based on the display attributes, descriptions or any object attribute defined in the object definition
2. Transport package add button - easy access to new package definition dialog
3. Package Definition Object - provides overview of the *PackageManager_PackageDefinition* objects as defined in the [Object Configuration](Object%20Configuration.md) model, package definition as well as the task definition have static fields for objects with display roles and description roles
4. Object quick actions toolbox - quick access to the object property editor dialog and key activities executed on the object (Data editing, save [[XML Template Editor]] shortcut or object delete). 
	1. Only Task Definition objects can get the xml template editor shortcut. Only the valid *Task Types* configured in the *"XMLTemplateTypes"* property of **TaskType** field are getting the shortcut visible (as defined in the  [Object Configuration](Object%20Configuration.md) model).
	2. Task Definitions are not having single "save" option, since all tasks are saved in one Package Definition file as children of the package object. Therefore save action is available only on the Package Definition object.
5. Task Definition Object - provides overview of the *PackageManager_TaskDefinition* objects as defined in the [Object Configuration](Object%20Configuration.md) model
6. Dynamic viewport grid of attributes selected for the tree views (as defined in the [Object Configuration](Object%20Configuration.md) model - object attributes configured with the *"ShowInTreeView": "True"* are dynamically listed here).
7. Context Menu - package definitions view have different context menus available depending on the object type. To avoid already overcrowded UI, most of the actions are done over context menus and drag/drop operations. Some of the actions in the context menu are working with multi-selected objects of the same class

![](screenshots/Pasted%20image%2020240124182404.png)

# Package Definitions View Actions

The package definition view provides a set of supported actions which should effectively help with the overall package management structure management.

## Create new definition objects

New package definitions can be created from the context menu or by using the "Add" button. 
If the current working directory is not configured, you will be prompted to do so - even if you do not decide to save the definition it is required to properly calculate the file paths etc.

![](screenshots/Pasted%20image%2020240124182910.png)

1. Form Generation is entirely driven with the [Object Configuration](Object%20Configuration.md) model 
2. Object fields configured with the *"**ShowInEditor**": "True"* are dynamically listed here).
3. The order of the fields is driven by the order of the field configurations in the object configuration model.
4. Fields marked as mandatory in the object configuration model are additionally displayed with the red asterisk in front of the value editor widget and if the value is not provided, form data will not be accepted when "OK" is clicked.
5. Placeholder texts are added for fields with no default value as defined in the object configuration model

## Modify object properties

Properties modification can be accessed by context menu or by clicking the "Properties" button and follows the same principles as in the [Create new definition objects](#Create%20new%20definition%20objects) 
After the form is generated, it is filled with the edited object data instead of the default data from the object model configuration.

![](screenshots/Pasted%20image%2020240124182928.png)

When the data changes are detected on form submission, the object will be marked on the tree view with asterisk in front of the object display and can be styled differently for better visibility (by default the left border is changed).
At this time the changes are not yet saved to the disk and live only in the tool. changes will be applied after clicking "Save" button.

![](screenshots/Pasted%20image%2020240124183008.png)

## Multi-Selected Object modifications

It is possible to modify multiple objects of the same object class (Package Definitions, package tasks).
When more than 1 item is selected in the package manager tree view, additional context menu entry will be available that lets the user change multiple objects with the same value.

![](screenshots/Pasted%20image%2020240124183124.png)

In this view you can select which columns you want to overwrite and this selection is taken over to the standard form data editor where the value settings can be adjusted:

![](screenshots/Pasted%20image%2020240124183148.png)

Last clicked item is taken as source object to determine what object class is being edited and which properties are available. This will also determine which objects will be modified as a result.

Source object is also used to pre-fill the form data initially so it is easy to overwrite data on multiple objects if we know the source object which is already set correctly.

## Save package definitions

Save action can be initiated with the "Save" button or from the context menu.
	**Note:** Context menu save action will work with multi-selected packages on the tree, while button works only for the given object definition.

Even if there are no changes to the package definition, the application will overwrite the file with the current [Object Configuration](Object%20Configuration.md) model. 

This is usually helpful if the data model configuration changes and you would like to generate default values for all objects in the model.
	**Note:** By default all fields are considered as exportable, only fields configured as *"IsForDataExport": "False"* are skipped.

**Note:** Adding tasks into [Execution Planner](Execution%20Planner.md) "copies" the current state of the transport task definition and its parent to provide the relevant data into the task execution queue. If the tasks are modified or relocated again after they were added to the queue it will be necessary to re-add them there post these actions.

### Definition Files management 

On saving the definition files and all required folder structures will be dynamically created where required so it is important that [Object Configuration](Object%20Configuration.md) model for fields of type "*FileInput*" is configured properly.

In case there are existing files in the working directory that would need to be relocated on saving (due to data patterns or attribute changes), application will generate new structures where required, move the files to target locations and delete old directories if they are left empty. Same conditions apply if the file name changes are detected.

If there are any leftover files that are not defined in the transport package definition, application will leave them behind.

## Drag and Drop - change package definitions and tasks order

In general the package manager does not have to sort by object name (this is actually a backup solution). 
If there is a dedicated field column which is defined with *"SortOrder"* role, objects will be sorted based on this attribute values.

The package tasks can be moved around in the hierarchy and between different package definitions but it is not supported yet to nest package definitions inside another package definition. 

Object relocations are typically causing data changes and therefore are marked as objects to be saved - it is especially important to save both, source and target definitions after all relocations are done since any existing file relocations will be executed along these actions as well. Not saving the source definition would mean that task definition "exists" in both locations which can be a good thing or a bad thing depending on what you need to achieve.

**Note:** Adding tasks into [Execution Planner](Execution%20Planner.md) "copies" the current state of the transport task definition and its parent to provide the relevant data into the task execution queue. If the tasks are modified or relocated again after they were added to the queue it will be necessary to re-add them there post these actions.

## Reload working directory

By pressing "**F5**" you can reload program configurations, stylesheet changes, object model configurations and the currently configured working directory structures.
Depending on your workstation and amount of data you have this might take a moment to reload everything again. 

**Note:** Any unsaved changes in the package definitions view are ignored - there might be some sort of handling in the future but right now it just reloads everything and shows the current state as defined in the json data files.

## Launch XML Template Editor

You can directly open the xml template editor view for the specific task definition by pressing the "Edit XML" button.

Button visibility is controlled by the [Object Configuration](Object%20Configuration.md) model of object class **PackageManager_TaskDefinition**.

Button is only available for valid objects of class **PackageManager_TaskDefinition** where the **TaskType** field configuration allows the task objects with specified task types to be edited by the template editor through the *"**XMLTemplateTypes**"* property.

**Note:** If XML Template Editor cannot open the file or the file does not exist, it will start new empty template editor and create the file if required.

## Filter definition objects 

Object filtering helps to find the relevant object definition by using its data. 
Filtering is started automatically when the text is changed in the input field - application will wait (by default 650ms) after the typing is finished and will start filtering automatically.

When the data is filtered and any child object matches the criteria, their parent is automatically selected as matching too, even if the parent does not meet the filter conditions.

Any spaces around filter criteria are stripped, so it is not required to write everything in one statement - " text 1, text 2 " will work exactly the same as "text 1,text 2" etc. 

Filters can be built according to the syntax options defined in the below sub-chapters. 

### Free Text Filtering

In this example objects where the display text or description text fits "text 1" or "text 2" will be listed:
	text 1, text 2

### Object Attribute Filtering

In this example only objects where the TaskType attribute fits "transport" or "schema" will be listed:
	tasktype: transport, schema

### Joined Attribute Filtering

All filtering conditions can be joined together with semicolon (";") to form the AND statement condition while comma works as the OR condition for the multi value filtering options.

In general any filtering conditions are case insensitive so the exact column name or value is not necessary, however only the values are queried, not respective display names of the attribute/value.

Following example will filter text 1 based on free text and make sure only objects with transport task type are shown:
	text 1, text 2; tasktype: transport, schema

# Package Manager Configuration

The package manager module has its own dedicated section in the application settings. It can be accessed by selecting the "Application Settings" button (**1**) from the side bar and navigating to the corresponding section in the program configuration(**2**). All currently supported configuration options will be listed in the central view (**3**).

![](screenshots/Pasted%20image%2020240124194144.png)