## Session Management ##

* MSSQL Connection support
* Add/Edit/Delete Sessions, Connect Database

## Transport Template Files Management 

* Open Transport definitions directory (set working directory)
* Create New Transport template definition
* Create New Object Transport Task
* Create New SQL Transport Task
* Read unsupported transport tasks
* Open Existing Transport Template files
* Parse XML Templates and Connect them with the database entries
* List objects from database by XObjectKey
* List objects from database tables, table filtering

## Object Relations Management ##

* List objects selected via table relations
* Load predefined database table relations
* Preselect object relations according to the database model
* Save existing object relations as presets
* Apply custom relation presets
* Dynamic listing of selected objects

## Template Definition Editing

* Drag and drop XML Structure objects to adjust order and hierarchy
* Bulk change supported transport flags or transport container flags
* Bulk apply relation presets
* Delete entries from the XML structure
  

## Transport Package Management

* Create Transport Package and Transport Task Definition
* Support flexible object model and filesystem structure definition
* Customizable display columns in tree view (name and descripton placeholders are always there, but additional fields can be added to display)
* Support file system operations (create, update, move, delete)
* Delete empty folders when deleting files
* Direct edit of xml transport templates only for task types configured as transporter type
* Manage transport package structure with drag and drop
* Object based filters, find package by display, description or any predefined attribute
* Drag and drop integration with execution planner (one direction only)
  
## Object configuration editor

* Universal object data editor tied to the object configuration model
* Allows to show only editable fields
* Support for most basic data inputs
* Defines which attributes are exported to the target JSON file
  
## Transport package execution planner 

* Powershell session integration
* OI Transport management tools integration
* Drag and drop tasks or task groups for execution
* Import or export transport packages
* Import schema extensions
* Run raw sql scripts - 
	* **While the program supports direct database connection and sql scripts execution, it is not advised to do this since you may break some of the logic that was built by One Identity on top of the database. Use only on your own risk.**
* Copy definition file to the export directory (where command is not defined for task type)
* Possibility to override the transport manager tool  commands for import/export tasks with custom powershell commands
* Start import/export tasks by single items or by group
* Queue transport management operations
* Support for AutoUpdate or Database Compiler execution after transport installation
* Create multiple execution plans

# Planned Features #

* Transport Template validation
* Transport template optimization and description validation
* Transport templates merging
* Find database objects by change label
* Convert existing change label tasks to object transport tasks
* Support for all other transport types (Sync Project, Change Label etc.)
* Support for the tree item edit operations (display names for tasks, containers, file names, folders etc.)
* Better management and application of the relation presets
* Configuration migration functionalities
* Application Settings View
* A lot of prompts, messageboxes and action confirmations
* UI and application layout improvements
    * Improve transport template editing layouts
* Dark mode/application theme configuration
* Transport template definition wizard - simplify the process of custom configurations migration to aid in the template generation
* Import/export relation presets
* Import/export execution plans

# Known Issues and Limitations #

This software has been built with maximum usability in mind and will have its own limitations during the development phase.
The goal is to have the overall structure of the whole application and work around the parts that are the most difficult/troubling to work with.
Any exception that program will catch is going to be thrown on the screen in the dedicated message box. This can help with bug fixing and understanding the issues system runs into. 

## What I know does not work too well right now ##

* Connecting to the database with wrong connection data will freeze the program until the timeout is reached
* If you do not decrypt the session data correctly and then create new connection, any previously saved session will be overwritten. There is no warning to that.
* There is totally no support for any other xml format than the one with structure of the transport template. Program will treat this as empty transport template.
* SQL script can be edited, but any XML comments left inside the text node will be deleted
* In some cases the comment descriptions above the containers are not deleted
* There is almost no validation to what you move around the xml structure - for now you need to know better not to add transport task into another transport task or sql task into object transport container.
* Object Relations cluster is sometimes weird in what it does (especially selecting relations using the database model). Also there is no hint on which relations you edit (database object or template object). This will get updated and organised better.
* Working directory is currently heavily used to work with package definitions, templates and should be always selected as first thing. There might be cases that it is not validated yet and program ends up calculating paths out of the transport management tool location instead of expected workdir.
* There is no indication that you have some unsaved changes in the template comparing to the original file.
* There is no auto save. You need to save each changed package definition manually when you move tasks across packages (multi select works though).
* Searching can sometimes break in syntax parsing (difficult to reproduce). Program might need a restart if that occurs.
* There is no aid in adjusting program or object configuration files yet, they need to be edited manually at the moment.