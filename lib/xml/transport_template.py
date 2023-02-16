from lxml import etree

class transport_template(object):

    def __init__(self, application):
        super(transport_template, self).__init__()
        self.application = application
        self.tasks = {}

        """ Root Node setup"""
        self.data = etree.Element("TransportTemplate")

        """ Tranport Header setup """
        self.header = etree.Element("Header")

        """ Transport description setup """
        self.description = etree.Element("Parameter")
        self.description.attrib['Name'] = "Description"
        self.description.text = "Transport Test Description"

        self.header.append(self.description)

        self.tasks = etree.Element("Tasks")

        """ Build the transport structure blocks """
        self.data.append(self.header)
        self.data.append(self.tasks)

    def to_string(self):
        etree.indent(self.data)
        return etree.tostring(self.data, pretty_print=True, encoding='unicode')

    def add_transport_task(self, task_class):
        new_task = transport_task(self.application, task_class)
        self.tasks.append(new_task.data)
        return new_task
    

class transport_task(object):
    
    def __init__(self, application, task_class):
        super(transport_task, self).__init__()
        self.application = application
        self.task_class = task_class

        """ Task Node setup"""
        self.data = etree.Element("Task")

        self.data.attrib["Display"] = self.task_class

        if self.task_class == "ObjectTransport":
            self.data.attrib["Class"] = "VI.Transport.ObjectTransport, VI.Transport"

    def add_container(self, base_object):
        container = task_container(self.application, base_object)
        self.data.append(container.data)
        return container
            
class task_container(object):
    def __init__(self, application, base_object):
        super(task_container, self).__init__()
        self.application = application
        self.base_object = base_object

        """ Main Container Node setup"""
        self.data = task_parameter(self.application, "Container").data
        base_object_node = task_parameter(self.application, "BaseObject").data
        base_object_table = task_parameter(self.application, "TableName", base_object.text(0)).data
        
        """ build the object container """
        self.data.append(base_object_node)

        base_object_node.append(base_object_table)
        base_object_node.append(task_parameter(self.application, "Display", base_object.text(0)).data)

        columns = task_parameter(self.application, "Columns").data
        columns.append(task_parameter(self.application, "ColumnName", base_object.text(0)).data)

        base_object_node.append(columns)



class task_parameter(object):
    def __init__(self, application, parameter_name, parameter_value = ""):
        super(task_parameter, self).__init__()
        self.application = application

        """ Container Node setup"""
        self.data = etree.Element("Parameter")
        self.data.attrib["Name"] = parameter_name
        self.data.text = parameter_value
