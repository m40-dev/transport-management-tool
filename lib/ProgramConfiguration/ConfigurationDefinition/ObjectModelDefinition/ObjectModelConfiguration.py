ObjectModelConfiguration = {
    "SectionName": "ObjectModelConfiguration",
    "IsEditable": False,
    "Description": "Object Model configuration parameters data",
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
            "FieldTypeExportMapping":{
                "Common":[
                    "RowId", 
                    "Display",
                    "Description",
                    "FieldType", 
                    "FieldRole", 
                    "DefaultValue", 
                    "PlaceholderText", 
                    "IsMandatory",
                    "ShowInEditor",
                    "ShowInTreeView", 
                    "IsForDataExport",
                    "UseTemplates"],
                "FieldType": {
                    "FixedInput":["Options"],
                    "IntegerInput":["MinValue","MaxValue"],
                    "FileInput":["FileSelectionMode", "RedirectDirectoryStatic", "RedirectDirectoryDynamic", "RedirectDirectoryRelativeTo"],
                    "ListInput":["Separator"],
                    "ChildObjectReference":["Class"],
                    "StringInput":["IsSensitive"]
                    },
                "FieldRole":{
                    "SortOrder": ["DistributeEvenly"]
                    },
                "ExecutionPlanner_ExecutionTask": {
                    "TaskType": ["Transporter", "SQLScript", "SchemaExtension"]
                    },
                "PackageManager_TaskDefinition": {
                    "TaskType": ["XMLTemplateTypes"]
                    },
                "UseTemplates":{
                    True: ["ValuePattern"]
                }
            },
            "FieldId":
                {
                    "FieldType": "StringInput",
                    "Display": "Field Id",
                    "Description": "Provides the unique key for the field in the object model data export."
                },
            "Display":
                {
                    "Display": "Display Name",
                    "Description": "Sets the field display name that will be used in the interface and form data editor.",
                    "FieldType": "StringInput",
                    "PlaceholderText": "Field Display name in the form"
                },
            "Description":
                {
                    "Display": "Field Description",
                    "FieldType": "TextInput",
                    "Description": "Sets the field description that will be visible as tooltip in the form data editor.",
                    "PlaceholderText": "Sets the field description that will be visible as tooltip in the form data editor."

                },
            "FieldType":
                {
                    "Display": "Field Type",
                    "FieldType": "FixedInput",
                    "DefaultValue": "StringInput",
                    "Options": {
                        "String": "StringInput", 
                        "Text": "TextInput",
                        "Number": "IntegerInput",
                        "Boolean": "BooleanInput",
                        "Child Reference": "ChildObjectReference",
                        "File Path": "FileInput",
                        "Predefined List": "FixedInput",
                        "Multivalue field":"ListInput"}
                },
            "IsMandatory":
                {
                    "Display": "Is Mandatory",
                    "FieldType": "BooleanInput",
                    "DefaultValue": False
                },
            "ShowInEditor":
                {
                    "Display": "Show in Form Editor",
                    "FieldType": "BooleanInput",
                    "DefaultValue": True
                },
            "ShowInTreeView":
                {
                    "Display": "Show in TreeView",
                    "FieldType": "BooleanInput",
                    "DefaultValue": False
                },
            "IsForDataExport":
                {
                    "Display": "Use in Export",
                    "FieldType": "BooleanInput",
                    "DefaultValue": True
                },
            "FieldRole":
                {
                    "Display": "Field Role",
                    "FieldType": "FixedInput",
                    "DefaultValue": "",
                    "Options": {
                        "Display Role": "DisplayRole", 
                        "Description Role": "DescriptionRole",
                        "Sort Order": "SortOrder",
                        "Unique Identifier": "UniqueIdentifier",
                        "": ""
                        }
                },
            "DefaultValue":
                {
                    "Display": "Default Value",
                    "FieldType": "StringInput",
                    "PlaceholderText": "Default field value"
                },
            "IsSensitive":
                {
                    "Display": "Contains Sensitive data",
                    "FieldType": "BooleanInput",
                    "DefaultValue": False,
                    "EditDependency": {"FieldType": "StringInput"}
                },
            "Separator":
                {
                    "Display": "Multivalue field Delimiter",
                    "FieldType": "StringInput",
                    "PlaceholderText": "Multivalue field Delimiter",
                    "EditDependency": {"FieldType": "ListInput"}
                },
            "Options":
                {
                    "FieldType": "TextInput",
                    "Display": "Values configuration",
                    "PlaceholderText": '{\n\t"Display Value 1": "Key1",\n\t"Display Value 2": "Key 2"\n}',
                    "EditDependency": {"FieldType": "FixedInput"}
                },
            "PlaceholderText":
                {
                    "FieldType": "StringInput",
                    "Display": "Placeholder Text",
                    "PlaceholderText": "Placeholder text visible in the text input box"
                },
            "UseTemplates":
                {
                    "Display": "Use Value Template",
                    "FieldType": "BooleanInput",
                    "DefaultValue": False,
                    "EditDependency": {}
                },
            "ValuePattern":
                {
                    "FieldType": "StringInput",
                    "Display": "Attribute value source mapping",
                    "Description": "Allows to transfer the source attribute value from the task definition object, use % mark as wrapping character to map other column value (%ColumnName%).\nParent column reference can be achieved with 'Parent.' prefix (%Parent.ColumnName%)",
                    "EditDependency": {"UseTemplates": True}
                },
            "MinValue":
                {
                    "Display": "Minimum Value Range",
                    "FieldType": "IntegerInput",
                    "EditDependency": {"FieldType": "IntegerInput"},
                    "PlaceholderText": "Minimum value range for the integer value"
                },
            "MaxValue":
                {
                    "Display": "Maximum Value Range",
                    "FieldType": "IntegerInput",
                    "EditDependency": {"FieldType": "IntegerInput"},
                    "PlaceholderText": "Maximum value range for the integer value"
                },
            "DistributeEvenly":
                {
                    "Display": "Distribute Values",
                    "FieldType": "BooleanInput",
                    "DefaultValue": False,
                    "EditDependency": {"FieldType": "IntegerInput", "FieldRole": "SortOrder"}
                },
            "Class":
                {
                    "Display": "Child Object Reference Class",
                    "FieldType": "FixedInput",
                    "DefaultValue": "",
                    "Options": {
                        "":"",
                        "Transport Task Definition": "PackageManager_TaskDefinition", 
                        "Transport Execution Task": "ExecutionPlanner_ExecutionTask"
                        },
                    "EditDependency": {"FieldType": "ChildObjectReference"}
                },
            "FileSelectionMode":
                {   
                    "Display": "File Selection Mode",
                    "FieldType": "FixedInput",
                    "DefaultValue": "FileName",
                    "Options": {
                        "File Name": "FileName", 
                        "Relative file path": "Relative",
                        "Absolute file path": "Absolute"
                        },
                    "EditDependency": {"FieldType": "FileInput"}
                },
            "RedirectDirectoryStatic":
                {
                    "FieldType": "StringInput",
                    "Display": "Static Directory location",
                    "Description": "Static directory location calculated from the relative root location.",
                    "EditDependency": {"FieldType": "FileInput", "FileSelectionMode": "FileName"}
                },
            "RedirectDirectoryDynamic":
                {
                    "FieldType": "StringInput",
                    "Display": "Dynamic Directory Pattern",
                    "Description": "Use attribute name inside % mark to build a dynamic directory location.(eg. Source_Files/%PackageName%)",
                    "EditDependency": {"FieldType": "FileInput", "FileSelectionMode": "FileName"}
                },
            "RedirectDirectoryRelativeTo":
                {
                    "Display": "Location Relative To",
                    "FieldType": "FixedInput",
                    "DefaultValue": "Parent",
                    "Description": "Configures the relative root location for the file path calculation.",
                    "Options": {
                        "Parent object": "Parent", 
                        "Working directory": "Workdir"
                        },
                    "EditDependency": {"FieldType": "FileInput", "FileSelectionMode": "FileName"}
                },
            "XMLTemplateTypes":
                {
                    "Display": "XML Template Types",
                    "FieldType": "ListInput",
                    "Description": "Configures the valid task types that can be edited with the XML Template Editor.",
                    "EditDependency": {"FieldId": "TaskType", "ConfigurationSectionId": "PackageManager_TaskDefinition"}
                },
            "Transporter": {
                    "Display": "Database Transporter tasks",
                    "Description": "Defines valid task types to be redirected into the database transporter tool in the execution planner.",
                    "FieldType": "ListInput",
                    "DefaultValue": ["Transport", "BugFix"],
                    "EditDependency": {"FieldId": "TaskType", "ConfigurationSectionId": "ExecutionPlanner_ExecutionTask"}
                },
            "SQLScript": {
                    "Display": "SQL Script tasks",
                    "Description": "Defines valid task types to be redirected into the raw sql script processing in the execution planner.",
                    "FieldType": "ListInput",
                    "DefaultValue": ["SQL"],
                    "EditDependency": {"FieldId": "TaskType", "ConfigurationSectionId": "ExecutionPlanner_ExecutionTask"}
                },
            "SchemaExtension": {
                    "Display": "Schema Extension tasks",
                    "Description": "Defines valid task types to be redirected into the raw sql script processing in the execution planner.",
                    "FieldType": "ListInput",
                    "DefaultValue": ["Schema"],
                    "EditDependency": {"FieldId": "TaskType", "ConfigurationSectionId": "ExecutionPlanner_ExecutionTask"}
                }
        },
    "ConfigurationSamples":{
        "StandardField":{
            "Display":"Standard Field",
            "Description":"Field with minimum configurations.",
            "FieldType":"StringInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide attribute value..",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False
        },
        "NameField":{
            "Display":"Object Name",
            "Description":"Standard object name used as the display name in the application.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide object name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "DescriptionField":{
            "Display":"Object Description",
            "Description":"Standard object description field.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide object description..",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "SortOrderField":{
            "Display":"Sort Order attribute",
            "Description":"Standard object attribute with sort order role.",
            "FieldType":"IntegerInput",
            "FieldRole":"SortOrder",
            "DefaultValue":"",
            "PlaceholderText":"Provide Sort Order id",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "MinValue":"",
            "MaxValue":"",
            "DistributeEvenly":False
        },
        "BooleanField":{
            "Display":"Boolean field attribute",
            "Description":"Standard boolean field.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":True,
            "PlaceholderText":"Boolean field attribute",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "PredefinedValueField":{
            "Display":"Predefined list of values",
            "Description":"Standard fixed value selection field.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"Option1Key",
            "PlaceholderText":"Provide object description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":"{\n\"Option 1 Display\": \"Option1Key\",\n\"Option 2 Display\": \"Option2Key\",\n\"\": \"\"\n}"
        },
        "StaticFileInputField":{
            "Display":"Static File location field",
            "Description":"File path attribute with static directory location relative to the parent directory.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"FileName.extension",
            "PlaceholderText":"Provide file name..",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"Target_Directory",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "DynamicFileInputField":{
            "Display":"Dynamic File location field",
            "Description":"File path attribute with dynamic directory location relative to the parent directory. Dynamic directory pattern determines the final file location in the system.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"FileName.extension",
            "PlaceholderText":"Provide file name..",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"Target_Directory/%DirectoryNameAttribute%",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "MultivalueField":{
            "Display":"Standard Multivalue field",
            "Description":"Field with multivalue data configuration(comma separated).",
            "FieldType":"ListInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide attribute value",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "Separator":","
        },
        "UniqueIdField":{
            "Display":"Unique identifier field",
            "Description":"Field with unique identifier configuration configurations.",
            "FieldType":"StringInput",
            "FieldRole":"UniqueIdentifier",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False
        },
        "ChildReferenceField":{
            "Display":"Standard Child reference field",
            "Description":"Field with child reference configuration.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide attribute value..",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "Class":"PackageManager_TaskDefinition"
        }

    }
}
