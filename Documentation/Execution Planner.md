Execution planner is a sub-component of the [Package Manager](Package%20Manager.md) which is primarily used to run the transport package operations directly from the Transport Management Tool UI.
Simply drop the package/task into the execution planner, select the right parameters and start the task.

Execution planner works synchronously in a way - it does not interrupt the UI, but the tasks are executed as defined in the planner order rather than simultaneously.

# Execution Planner View
Execution Planner view have following components defined:
1. **Execution Group node** - execution planner organizational node
2. **Execution Group toolbox** - quick access to the execution group operations 
3. **Execution Task node** - overview of the execution task and its properties
4. **Execution Task toolbox** - quick access to the execution task configuration parameters
5. **Execution Planner kill switch** - allows termination of the running execution planner queue 
6. **Execution Planner console** - provides the output from the process runner
![](screenshots/Execution%20Planner%20View.png)

# Execution Planner actions
The execution planner view is meant to provide quick access to the transport task executions. This chapter collects all currently available planner actions.

## Add Execution groups
There are two ways of creating an execution group:
	* use context menu in the execution planner view
	* drag and drop a Package Definition into the Execution Planner view to create an execution group together with execution tasks under this package - this feature works together with package filtering so only filtered items will be included.

## Add Execution tasks 
Since the planner is entirely dependent on the Package manager at the moment, the only way to add execution tasks is to drag it from the package manager view.
Task Definition item provides all the required parameters and information required to form an execution task.

## Organize task execution order
You can change the order of items with simple drag and drop operations.
Hierarchical structure is allowed here to better organize the execution workflow. 

## Adjust execution planner object parameters
You can adjust the execution planner object parameters before running the task - keep in mind that these changes will not have any effect on the original task definition.
Right click on the task you would like to modify and select appropriate action from the context menu.
Fields and options available here are driven by the [Object Configuration](Object%20Configuration.md) of the Execution Task object class.

## Start Single Execution Task
To start the single task, use the "Start task" button located in the **Execution Task toolbox**. 
In case there are already running tasks, application will queue this task for execution in the end of the current plan.

## Start Execution Group
To start the single task, use the "Start task" button located in the **Execution Task toolbox**.
In case there are tasks running already, process runner will queue all tasks in this group for execution at the end of the currently running execution plan according to the order defined in the plan.
If there are nested execution groups, they will be processed in the same order as defined in the view.
Example below shows how the planner will queue the tasks if the top level execution group is started:
1. first child object is an execution task so it is started
2. Package 1 is an Execution group item so all of its children are added to the execution queue as next
3. Package 2 is an Execution group item so all of its children are added to the execution queue as next
The same logic is applied recursively until the end of the tree is reached. 
![](screenshots/Execution%20Planner%20Start%20order.png)

## Stop Plan Execution
In case of errors or unexpected behaviour of the transport task executions you can quickly terminate the task executions with the "Stop Execution" button which will stop immediately all activities and clear the execution queue.
Please keep in mind that if this action is done in the middle of database compilation you might introduce some issues here.

# Execution Planner Tasks
In general the execution planner can run the tasks queued in the view, but also will run any additionally required tasks according to the execution task definition.
Depending on the task type the planner will determine which One Identity Tool to use to run the activity (configuration of the tool mappings is in the [Object Configuration](Object%20Configuration.md) of the Execution task object class).

If any **Import** task is executed, the compiler option and autoupdate options are checked to determine if additional tasks are required to be executed post the import action:
- AutoUpdate is checked - execution planner will add the AutoUpdate command into the task execution script
- CompilerOption is not None - execution planner will add the Database Compilation command into the task execution script

These operations are always checked and added in this order, so if there is an autoupdate and database compilation required, the autoupdate will be always ran before the compilation.

# Execution Planner Custom Configuration
Custom configuration of the execution planner allows you to run the custom import or export scripts where the standard behaviour of the application is not enough.
![](screenshots/Execution%20Planner%20Configuration.png)

When all of the local session variables are prepared, the "Task Execution Preparation Script" is executed first to initialize any custom modules or task preparatory operations - this script is executed every time regardless of the operation type.
If the Import or Export task commands are configured, application will use them instead of the direct one identity tools execution.

## Custom Session variables
When execution task is started, new powershell session is created which prepares all the execution task variables (as defined in the [Object Configuration](Object%20Configuration.md) for the execution task object class).

Application variables:
	**Workdir** - gives the information about the current working directory location of the package management module. 

Object configuration variables:
	**Connection** - only connection name is provided as the variable, connection details are not exposed in the session variables.
	All other predefined object attributes are passed to the powershell session as defined in the [Object Configuration](Object%20Configuration.md)


# Execution Planner Error handling
There is no error handling in the process runner at the moment, however it is planned to build it together with better execution status indicators (right now it just displays the text in bottom right corner of the task).
If there is an error in the task execution, process runner will move on to the next task like nothing happened.