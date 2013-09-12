from Cheetah.Template import Template
import os
import sys
import xml.etree.ElementTree as ET


class Attribute(object):

    def __init__(self, element=None):
        if element is not None:
            self.name = element.get("name")
            self.scope = element.get("ownerScope")
            self.visibility = element.get("visibility")
            self.id = element.get("xmi.id")
            self.type = ""
        else:
            self.name = ""
            self.scope = ""
            self.visibility = ""
            self.id = ""
            self.type = ""

    def __repr__(self):
        return ' '.join([self.visibility, self.name, self.type])


class Method(object):

    '''
        @deprecated
    '''

    def __init__(self, element):
        self.name = element.get("name")
        self.scope = element.get("ownerScope")
        self.visibility = element.get("visibility")
        self.id = element.get("xmi.id")

    def __repr__(self):
        return ' '.join([self.visibility, self.name])


class Class(object):

    def __init__(self, element):
        self.name = element.get("name")
        self.visibility = element.get("visibility")
        self.isAbstract = element.get("isAbstract")
        self.id = element.get("xmi.id")
        self.parent = ""
        self.attrs = []
        self.methods = []  # @deprecated

    def __str__(self):
        return '''{self.visibility} {self.parent} {self.name}\nisAbstract: {self.isAbstract}
\t{self.attrs}\n\t{self.methods}'''.format(self=self)

    def __repr__(self):
        return self.__str__()


try:
    tree = ET.parse(sys.argv[1])
except:
    raise Exception('''Programa invocado de forma incorreta.
                    Por favor digite no formato:
                     python testeModificado_v0.5.1 NomeDoXmi.xmi ''')
def_tree = ET.parse('default-uml14.xmi')
#tree = ET.parse('teste.xmi')

root = tree.getroot()

pacote = root.findall(
    './/{org.omg.xmi.namespace.UML}Model')[0].get("name")

try:
    os.makedirs('{0}/dto'.format(pacote))
    os.makedirs('{0}/dao'.format(pacote))
    os.makedirs('{0}/bo'.format(pacote))
except Exception as e:
    pass
finally:
    os.chdir('{0}/dto'.format(pacote))

classes = root.findall(
    './/{org.omg.xmi.namespace.UML}Namespace.ownedElement/{org.omg.xmi.namespace.UML}Class')

data_types = def_tree.findall('.//{org.omg.xmi.namespace.UML}DataType') +\
    def_tree.findall('.//{org.omg.xmi.namespace.UML}Enumeration') +\
    classes

dict_data_types = {elem.get("xmi.id"): elem.get("name") for elem in data_types}

dicionario_classes = {}
for class_ in classes:
    dicionario_classes[class_.get("xmi.id")] = Class(class_)
    #classifier = class_.getElementsByTagName("UML:Classifier.feature")

    attrs = class_.findall('.//{org.omg.xmi.namespace.UML}Attribute')
    for attr in attrs:
        # print 'attr ->',attr
        att = Attribute(attr)
        for type_ in attr.find('{org.omg.xmi.namespace.UML}StructuralFeature.type'):
            str_type = type_.get("href") or type_.get("xmi.idref")
            str_type = str_type[str_type.find('#') + 1:]
            att.type = dict_data_types[str_type]
            dicionario_classes[class_.get("xmi.id")].attrs.append(att)

associations = root.findall(
    './/{org.omg.xmi.namespace.UML}Namespace.ownedElement/{org.omg.xmi.namespace.UML}Association')


firstDict = {}
lastDict = {}
for association in associations:

    assoc = []

    associationsEnd = association.findall(
        './/{org.omg.xmi.namespace.UML}AssociationEnd')



    for associationEnd in associationsEnd:
        #print associationEnd
        infoAssoc = []

        multiplicityRange = associationEnd.find(
            './/{org.omg.xmi.namespace.UML}MultiplicityRange')
        clazzID = associationEnd.find(
            './/{org.omg.xmi.namespace.UML}AssociationEnd.participant/{org.omg.xmi.namespace.UML}Class').get("xmi.idref")

        infoAssoc.append(multiplicityRange.get("upper"))

        infoAssoc.append(dicionario_classes[clazzID].name)


        assoc.append(infoAssoc)


    first = assoc[0]
    last = assoc[-1]

    attInicio = Attribute()  # criando atributo da association
    attInicio.name = last[-1].lower()

    assocName = association.get("name")
    if assocName:
        attInicio.name = association.get("name")
    attInicio.visibility = "private"

    attInicio.type = last[-1]
    if last[0] == '-1':
        # print 'here'
        attInicio.type = "list,%s" % last[-1]

    attFim = Attribute()
    attFim.name = first[-1].lower()
    attFim.visibility = "private"

    attFim.type = first[-1]
    if first[0] == '-1':
        attFim.type = "list,%s" % first[-1]

    # print first, first[-1],' tem ',last[0],last[-1]
    # print last,last[-1],' tem ',first[0],first[-1]


    #tt = raw_input()


    # print attInicio
    # print attFim

    for d in dicionario_classes:
        clazz = dicionario_classes[d]
        if clazz.name == first[-1]:
            if (attInicio.name,attFim.name) not in firstDict:
                firstDict[(attInicio.name,attFim.name)] = 1

                if attInicio.name != clazz.attrs[-1].name:
                    clazz.attrs.append(attInicio)
        if clazz.name == last[-1]:
            if (attFim.name,attInicio.name) not in lastDict:
                lastDict[(attFim.name,attInicio.name)] = 1
                if attFim.name != clazz.attrs[-1].name:
                    clazz.attrs.append(attFim)


generalizations = root.findall(
    './/{org.omg.xmi.namespace.UML}Namespace.ownedElement/{org.omg.xmi.namespace.UML}Generalization')

for g in generalizations:

    childID = g.find(
        './/{org.omg.xmi.namespace.UML}Generalization.child/{org.omg.xmi.namespace.UML}Class').get("xmi.idref")
    parentID = g.find(
        './/{org.omg.xmi.namespace.UML}Generalization.parent/{org.omg.xmi.namespace.UML}Class').get("xmi.idref")

    # print childID
    # print parentID
    dicionario_classes[childID].parent = dicionario_classes[parentID].name
    # print dicionario_classes[childID].name,
    # 'extends',dicionario_classes[childID].parent


# print first
# print last


# os.chdir("dao")
for clazz in dicionario_classes.values():

    f = open("%sDTO.java" % clazz.name, "w")
    t = Template(file='../../templateDTO.impl', searchList=locals())
    f.write(str(t))
    f.close()

    os.chdir('../dao')
    f = open("%sDAO.java" % clazz.name, "w")
    t = Template(file='../../templateDAO.impl', searchList=locals())
    f.write(str(t))
    f.close()

    os.chdir('../bo')
    f = open("%sBO.java" % clazz.name, "w")
    t = Template(file='../../templateBO.impl', searchList=locals())
    f.write(str(t))
    f.close()
    os.chdir('../dto')
