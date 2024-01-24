# Transport Management Tool

![200](./lib/ui/img/icons/ApplicationIcon_Small.png)

The transport management tool is an utility tool to work with the XML template files for the database transporter used in the One Identity Manager as well as the interface to organize and manage transport package operations between administered systems.

While this is very specific use case, the goal is to improve the performance and reliability when building templates or working with transport package operations in general (a little bit of automation never hurts).

With time, the tool will grow with additional features(see documentation), but biggest focus right now is to get the base platform running with core features that make it useful already and help in the typical day to day activities.

From version 0.9, transport management tool uses components for custom window decorations based on the **CustomWindow** project

Sources:
* https://github.com/re7gog/CustomWindow

## How do I get set up?

* Install MSSQL Driver for the database connection support (Microsoft: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

    It is not required if you will use the tool in offline mode only.

* Download the latest Transport Management Tool package (7z file) from Downloads page (https://bitbucket.org/emergencycode/transport-management-tool/downloads/)

* Extract the package and run the application (TransportManager.exe) - there is no windows installer, tool works in the "portable" mode only.

## Current Features

List of Currently implemented features and available documentation can be found in the [Documentation](./Documentation/Readme.md) section.

There is no warranty coming with this software, please do your own testing, research when it comes to the transport management operations in One Identity Manager (also do your database backups).

## Issues, Bug Reports, Feature Requests

You can post your bug reports, issues, suggestions and feature requests in the [Issue Tracker](https://bitbucket.org/emergencycode/transport-management-tool/issues/new)

## Contact

This project is developed and maintained by a single person in free time only, 

if you have other inquiries related to the project, you can reach me by mail: transport-management-tool@proton.me.

## LICENSE

This project is an open source code under GPL v3, see [LICENSE](./LICENSE)