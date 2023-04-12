# README #

This README would normally document whatever steps are necessary to get your application up and running.


### How do I get set up? ###

* Install MSSQL Driver for the database connection support (installer saved in downloads)
* Extract the 7z file and run the application (TransportManager.exe)

### Current Features ###
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

### Planned Features ###
* Transport Template validation
* Transport template optimization and description validation
* Transport template merging
* Transport files management 
    * Manage Directory operations
    * Manage File operations
* Better Transport package definition
* Integration with the transport tools to import/export packages from UI
* Built-in terminal for the transport operations output
* Better management and application of the relation presets
* Search queries for the package definitions
* Configuration migration functionalities
* Application Settings View
* A lot of prompts, messageboxes and confirmations
* UI and application layout improvements
* ...