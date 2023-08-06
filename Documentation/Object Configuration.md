The object model for the package manager is driven with the dedicated JSON file which provides the input to the tool about the structure and model of the transport package as required in your environment.

Default configuration with some mandatory field configurations is provided with the program files (*object_configuration_default.json*) and can be used to provide the custom object model configuration to the program.
Custom file must be named "*object_configuration.json*" to be properly loaded by the application.

# Object Configuration 
There are predefined object classes that can be supported by the application and need to be defined for the tool to work properly.
Each object class have to have minimum fields configured in order to drive the data model and functionalities built into the program.

### PackageManager_PackageDefinition

Defines the transport package object. Key columns and parameters are described here, full definition can be seen in the repository or in the local directory of the application.

```
"PackageManager_PackageDefinition":                                    # Fixed Object Class Name
    "DefinitionFile":                                                  # Field Name
        {                                                              
            "FieldType": "FileInput",                                  # Defines the field to be the file input type 
            "Display": "Definition File Name",                         # Display name of the field
            "DefaultValue": "definition.json",                         # Initial json file name
            "IsForDataExport": "False",                                # Do not save this field information in the export data
            "FileExtension": "*.json",                                 # File extension to set on the file selection dialog
            "FileSelectionMode": "FileName",                           # Defines the file selection mode for the application (only file name to be used)
            "RedirectDirectoryDynamic": "Source_Files/%PackageName%",  # Defines the dynamic directory pattern to calculate the definition file location
            "IsMandatory": "True"                                      # Marks the field value as mandatory
        },                                                             
    "ChildTasks":                                                      # Children column
        {                                                              
            "FieldType": "ChildObjectReference",                       # Set the field to object reference
            "Class": "PackageManager_TaskDefinition",                  # Allowed Target object class name
            "ShowInEditor": "False"                                    # Do not display the column in editor
        }
```

Mandatory fields:
	**DefinitionFile** - provides the Json file information for the application. This file will be tracked and then updated with the export data on save.
	**ChildTasks** - column name is not relevant but this is somewhat mandatory to provide one column where the child object reference is stored. This will basically tell the application where to store the child task information. 

### PackageManager_TaskDefinition

Defines the transport package task object. Key columns and parameters are described here, full definition can be seen in the repository or in the local directory of the application.

```
"PackageManager_TaskDefinition":                                                              # Fixed Object Class Name
        {
        "TaskType":                                                                           # Field Name
            {                                                                                 
                "FieldType": "FixedInput",                                                    # Configure the field as Fixed Input (Drop down list)
                "Options": {"Transport Package": "Transport",                                 # Allowed options to be selected by the user
							"SQL Script": "SQL",                                              # Options need to be provided in the "Display Name": "Expected Field Value" format
							"Schema Extension": "Schema",                                     
							"Bug Fix Package": "BugFix"},                                     
                "DefaultValue": "Transport",                                                  # Initial field value
                "Display": "Task Type",                                                       # Display name of the field
                "ShowInTreeView": "True",                                                     # Information for the application to show the column in the viewport
                "IsMandatory": "True",                                                        # Marks the field value as mandatory
                "XMLTemplateTypes": ["Transport", "BugFix"]                                   # Tells the program which task types can be edited with the integrated xml template editor. 
																					            This is special property of this field (does not work with any other fields)
            },                                                                                
        "DefinitionFile":                                                                     # Field Name
            {                                                                                 
                "FieldType": "FileInput",                                                     # Defines the field to be the file input type 
                "FileSelectionMode": "FileName",                                              # Defines the file selection mode for the application (only file name to be used)
                "RedirectDirectoryStatic": "Task_Definitions",                                # Defines the static directory name to redirect the file location
                "RedirectDirectoryRelativeTo": "Parent",                                      # Defines the static directory root. "Parent" will set the root of task files under the parent PackageDefinition directory
                "IsMandatory": "True",                                                        # Marks the field value as mandatory
                "ShowInTreeView": "True"                                                      # Information for the application to show the column in the viewport
            },                                                                                
        "ExportFile":                                                                         # Field Name
            {                                                                                 
                "FieldType": "FileInput",                                                     # Defines the field to be the file input type 
                "FileSelectionMode": "FileName",                                              # Defines the file selection mode for the application (only file name to be used)
                "RedirectDirectoryDynamic": "Package_Data/%Parent.PackageName%/%TaskType%"    # Defines the dynamic directory pattern to calculate the definition file location
            },                                                                                
        "CompilerOption":                                                                     # Field Name
            {                                                                                 
                "FieldType": "FixedInput",                                                    # Configure the field as Fixed Input (Drop down list)
                "Options": {"No Compilation": "None",                                         # Allowed options to be selected by the user
							"Full Compilation": "Full",                                       # Options need to be provided in the "Display Name": "Expected Field Value" format
							"Skip Web Projects Compilation":"NoWeb"},                         
                "DefaultValue": "NoWeb",                                                      # Initial field value
                "ShowInTreeView": "True"                                                      # Information for the application to show the column in the viewport
            },                                                                                
        "AutoUpdate":                                                                         # Field Name
            {                                                                                 
                "FieldType": "BooleanInput",                                                  # Configure the field as Boolean Input (Checkbox)
                "DefaultValue": "False"                                                       # Initial field value
            }
```

Mandatory fields:
	**DefinitionFile** - Provides information about the source file for the transport package to be generated.
	**ExportFile** - Provides information about the target file for the transport package to be generated.
	**TaskType** - Defines type of the transport task to determine the right tool to use. The **XMLTemplateTypes** parameter on this field defines which task types can be directly edited in the integrated xml template editor.
	**CompilerOption** - Defines whether the database needs to be compiled after the installation of the transport package.
		Supported options are:
				- "*None*" - No compilation required
				- "*NoWeb*" - Skip web portal modules
				- "*Full*" - Full compilation
	**AutoUpdate** - Defines whether the local workdir needs to be updated before the database compilation/after transport package installation. This is usually helpful when uploading custom files to the database with the transport that will be required in the compilation. 

### ExecutionPlanner_ExecutionGroup

Defines the Execution Planner group object. Groups are used to structure the activities in the execution planner and run tasks accordingly.

```
"ExecutionPlanner_ExecutionGroup":                                 # Fixed Object Class Name
            {                                                      
            "ExecutionTasks":                                      # Field Name
                {                                                  
                    "FieldType": "ChildObjectReference",           # Set the field to object reference
                    "Class": "ExecutionPlanner_ExecutionTask",     # Allowed Target object class name
                    "ShowInEditor": "False"                        # Do not display the column in editor
                }                                                  
            }  
```

Mandatory fields:
	**ExecutionTasks** - defines the child task objects reference. This will basically tell the application where to store the execution task information.

### ExecutionPlanner_ExecutionTask

Defines the execution task to be ran by the planner. The execution task is typically drag/dropped into the planner so most of the fields are directly mapped to the execution task.
There are similar configuration requirements as for the task definition, but we can additionally define the data source mapping and any additional attributes that will be used by the process runner.

```
"ExecutionPlanner_ExecutionTask":                            # Fixed Object Class Name
            {
			"TaskType":                                      # Column name
                {                                            
                    "FieldType": "StringInput",              # Makes the field visible and editable in the form editor
                    "Source": "TaskType",                    # Source of the value information, data is mapped from the dropped PackageManager_TaskDefinition
                    "Transporter": ["Transport", "BugFix"],  # Information for the application to match the task types with the database transporter CMD tool
                    "SQLScript": ["SQL"],                    # Information for the application to match the task types with the SQL Script task (direct SQL execution)
                    "SchemaExtension": ["Schema"],           # Information for the application to match the task types with the Schema Extension CMD tool
                    "ShowInTreeView": "True"                 # Information for the application to show the column in the viewport
                } 
		}
```

Mandatory fields:
	**TaskType** - Defines the task type to determine which tool to use when executing the task. 
	**Connection** - Defines the connection name to be used with the task execution.
	**DefinitionFile** - Source file with the transport template, sql script, schema etc
	**ExportFile** - Target file created during the task execution
	**CompilerOption** - System Compilation flag to run after import task execution
	**AutoUpdate** - local workstation update after transport import task execution

Field values are typically mapped from the corresponding Task Definition (see chapter: Execution task attribute mappings). 
Any fields defined in the execution task will be then available in the execution runner session as powershell variable under column name defined in the execution task fields configuration.

# Field configurations

Example field configuration with general options, also described in the above examples.

```
"Field_Name":                                                # Target Column Name of the object
            {                                                
                "FieldType": "StringInput",                  # Field Type definition. Possible options defined below.
                "Display": "Package Name",                   # Display Name of the field (Label in form)
                "PlaceholderText": "Provide Package Name",   # Placeholder text for the text inputs
                "FieldRole": "DisplayRole",                  # Field Role defines the purpose of the field. Possible options defined below.
                "IsMandatory": "True",                       # Marks the mandatory field in the form editor
                "IsForDataExport": "False",                  # Excludes the column from the target object data export
                "DefaultValue": "Initial Field Value",       # Provides the initial value for the field
                "ShowInTreeView": "True"                     # Information for the application to show the column in the viewport
				"ShowInEditor": "False"                      # Information for the editor to show the field in the editor
            }                                                
```

## Field Types

Field types are providing the information to the editor on which editor to use. Only supported field types can be displayed in the form.

### String Input

Provides the standard line edit widget (single line) to enter the value.

```
"FieldType": "StringInput"
```

### Text Input

Provides the rich text editor widget to enter the data (usually description fields). Gives 3-4 line viewport to insert the field value. 

```
"FieldType": "TextInput"
```

### Integer Input

Provides standard line edit widget (single line) to enter the value but the field is having the integer mask configured.

```
"FieldType": "IntegerInput"
```

### File Input

Provides standard line edit widget (single line) to enter the value and the button to select the file using standard file system dialog.
File input modes are going to determine the location of the files in the system and are usually tricky if the model is not configured according to the actual situation in the filesystem (tool calculates other paths based on these parameters).

```
"FieldType": "FileInput",                                  # Defines the field to be the file input type 
"FileExtension": "*.json",                                 # File extension to set on the file selection dialog
"FileSelectionMode": "FileName",                           # Defines the file selection mode for the application 
"RedirectDirectoryDynamic": "Source_Files/%PackageName%",  # Defines the dynamic directory pattern to calculate the definition file location
"RedirectDirectoryStatic": "Task_Definitions",             # Defines the static directory name to redirect the file location
"RedirectDirectoryRelativeTo": "Parent"                    # Defines the static directory root. "Parent" will set the root of task files under the parent PackageDefinition directory

```

There are following file selection modes supported:
	**FileName** - User selects the file but only the file name is taken. 
	**Relative** - Relative path to the working directory is calculated.
	**Absolute** - Absolute path in the filesystem is taken as-is. 

**RedirectDirectoryDynamic** and **RedirectDirectoryStatic** are excluding each other. If both are provided, application will use the static directory location instead of dynamic (less calculations needed).
Dynamic directory locations can be built from the pattern where the exact object column names are provided inside the '**%**' symbols.

**RedirectDirectoryStatic** will calculate directory in relation to the current working directory or if required to the parent definition location *("RedirectDirectoryRelativeTo": "Parent")*

Based on these patterns and configurations, the Transport Management tool will automatically create, relocate and delete files when these changes are requested. Same configuration will be used when the dependent objects are updated and file paths would change because of that - not only definition file is tracked but any field of this type.  

### Fixed Input

Provides the combo box (drop down list) with the predefined options to select from the editor. 
```
"FieldType": "FixedInput",                                                    # Configure the field as Fixed Input (Drop down list)
"Options": {"Transport Package": "Transport",                                 # Allowed options to be selected by the user
			"SQL Script": "SQL",                                              # Options need to be provided in the "Display Name": "Expected Field Value" format
			"Schema Extension": "Schema",                                     
			"Bug Fix Package": "BugFix"}
```
### Boolean Input

Provides checkbox widget to get the boolean value from the editor.
```
"FieldType": "BooleanInput"
```
### Child Object Reference

Provides information on how to build hierarchical structure of the Transport Management Tool objects. 
This field type does not have a supported user interface in the editor form.
```
"FieldType": "ChildObjectReference",             # Field Type definition
"Class": "PackageManager_TaskDefinition"         # Allowed Child Object Class
```

## Field Roles

Field role defines role of the field value in the application (display, description) but also are used to declare other field roles for the application to generate or manage accordingly (like unique identifiers or sort order). 

### Display Role

Marks the field value as display to be shown in the data display widgets. Multiple columns with the display role will be concatenated.
```
"FieldRole": "DisplayRole"         # Field display role definition
```

### Description Role

Marks the field value as display to be shown in the data display widgets. Multiple columns with the description role will be concatenated.
```
"FieldRole": "DescriptionRole"     # Field description role definition
```

### Unique Identifier

Generate Unique Identifier (UUID4) for the object. 
This UID is generated when the editor is opened for new or existing object, or during the data export for fields with no value available.

```
"FieldType": "StringInput",       # Field type for the editor view
"FieldRole": "UniqueIdentifier"   # Unique Identifier role definition
```

### Sort Order

Sort order defines the organization attribute to put the items on the lists but also generate the appropriate order identifiers for the transport actions where required.
Sort order can be driven purely by the row position in the view or determined by the minimum and maximum values for the application to calculate. 

``` 
"FieldType": "IntegerInput",   # Field type for the editor and data type
"FieldRole": "SortOrder",      # Sort order role definition
"MinValue": 100,               # Minimum sort order value
"MaxValue": 999,               # Maximum sort order value
"DefaultValue": 100,           # Initial value
"DistributeEvenly": "True",    # Use space between items to distribute the sort order evenly 
```

## Other options

This section describes the options not listed in the above sections.

### ShowInEditor

Defines if the parameter is editable in the editor interface. This is typically used to let the generated or structural widgets out of the user interface and just let the data work.
By default all fields will be shown as long as the input type is supported.
```
"ShowInEditor": "False"                      # Information for the editor to show the field in the editor
```

### IsForDataExport

This parameter defines if the field should be added in the export data when the file definition is saved. By default all fields are marked for export so this parameter is not required unless you want to exclude the field. 
```
"IsForDataExport": "False",                  # Excludes the column from the target object data export
```

### ShowInTreeView

This parameter defines if the field should be added in the viewport data. By default all fields are hidden and only required fields need this attribute to be set.
```
"ShowInTreeView": "True"                     # Information for the application to show the column in the viewport
```

The viewport of the display widgets is structured the same way for similar items, display roles show the object label, description role attributes are filling the description space and any additional attributes to be shown in the viewport are dynamically added under the description in a 4 column layout: 
![](screenshots/Transport%20Package%20Task%20View.png)

## Execution task attribute mappings

Section dedicated only to the attribute mapping configuration in the execution task model.
When the transport package task is dropped into the execution planner, it is saved in the last known condition together with the parent package definition to allow the execution task construction according to the local requirements.

### Package Definition reference 

Source value can be referred as **PARENT_DEF**.*parent_column_name* to map the original parent package definition values with the execution task.
```
"ParentDescription":
	{
		"FieldType": "StringInput",
		"Source": "PARENT_DEF.Description"
	}
```
### Task Definition reference

Source value referred just by the task definition column name. In this example the **TaskName** column value defined in the **PackageManager_TaskDefinition** source object class will be mapped with this field and exported to the process runner session as **ExecutionTaskName**.
```
"ExecutionTaskName": 
	{
		"FieldType": "StringInput",
		"Source": "TaskName"
	}
```

### Task Type Configuration

Task type is having additional parameters that are not supported in any other field since it is used to determine the tool or right action to execute when process runner is working through the tasks.
```
"TaskType":                                     # Execution Task Field
	{                                           
		"FieldType": "StringInput",             # Field Type
		"Source": "TaskType",                   # Source column name to map values
		"Transporter": ["Transport", "BugFix"], # Information for the application to match the task types with the database transporter CMD tool
		"SQLScript": ["SQL"],                   # Information for the application to match the task types with the SQL Script task (direct SQL execution)
		"SchemaExtension": ["Schema"],          # Information for the application to match the task types with the Schema Extension CMD tool
	}
```

