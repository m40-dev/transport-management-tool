# README #

Transport Manager Tool is an attempt to provide some UI to the XML template definitions and also simplify or automate some transport related activities in One Identity Manager.

With time, the tool will grow with additional features, but the most focus is set on the usability and aid in the typical day to day applications.

## How do I get set up? ##

* Install MSSQL Driver for the database connection support (installer saved in downloads)
* Extract the 7z file and run the application (TransportManager.exe)
* Open existing transport template or start building new one

# Current Features #
List of Currently implemented features grouped into feature categories.

## Session Management ##
* MSSQL Connection support
* Add/Edit/Delete Sessions, Connect Database
* List objects from database by XObjectKey
* List objects from database tables, table filtering

## Transport Template Files Management ##
* Open Transport definitions directory (set working directory)
* Create New Transport template definition
* Create New Object Transport Task
* Create New SQL Transport Task
* Read unsupported transport tasks
* Open Existing Transport Template files
* Parse XML Templates and Connect them with the database entries

## Object Relations Management ##
* List objects selected via table relations
* Load predefined database table relations
* Preselect object relations according to the database model
* Save object relations as preset

## Template Definition Editing ##
* Drag and drop XML Structure objects to adjust order and hierarchy
* Bulk change supported transport flags or transport container flags
* Bulk apply saved relations preset
* Delete entries from the XML structure

# Planned Features #
* Transport Template validation
* Transport template optimization and description validation
* Transport templates merging
* Find database objects by change label
* Convert existing change label tasks to object transport tasks
* Integration with the transport tools to import/export packages from UI
* Support for all other transport types (Sync Project, Change Label etc.)
* Transport Package Execution Planner
* Built-in terminal for the transport operations output
* Transport files management 
    * Manage Directory operations
    * Manage File operations
* Better Transport package definition
    * More attributes to define the package
* Support for the tree item edit operations (display names for tasks, containers, file names, folders etc.)
* Better management and application of the relation presets
* Search Transport Template Definitions
    * By Name
    * By Description
    * By Base Object UID
* Configuration migration functionalities
* Application Settings View
* A lot of prompts, messageboxes and action confirmations
* UI and application layout improvements
    * Improved control over transport task options 
* Dark mode

# Known Issues and Limitations #
This software has been built with maximum usability in mind and will have its own limitations during the development phase.
The goal is to have the overall structure of the whole application and work around the parts that are the most difficult/troubling to work with.
Any exception that program will catch is going to be thrown on the screen in the dedicated message box. This can help with bug fixing and understanding the issues system runs into.

**What I know does not work too well right now:**

* Connecting to the database with wrong connection data will freeze the program until the timeout is reached
* If you do not decrypt the session data correctly and then create new connection, any previously saved session will be overwritten. There is no warning to that.
* There is totally *no* support for any other xml format than the one with structure of the transport template
* SQL script can be edited, but any XML comments left inside the text node will be deleted
* In some cases the comments above the containers are not deleted
* There is almost no validation to what you move around the xml structure - for now you need to know better not to add transport task into another transport task or sql task into object transport container.
* Object Relations cluster is sometimes weird in what it does (especially selecting relations using the database model). 
* Working directory is currently used more for the sake of opening different files faster/easier - manual saving still sends us into other locations
* There is no prompt when switching transport template and not saving the current one
* There is no indication that you have some unsaved changes in the template comparing to the original file.