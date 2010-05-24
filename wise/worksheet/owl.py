#output RDFA/OWL ontology

from xml.dom import minidom


def generate(icls):


    xml = minidom.Document()

    rdf = xml.createElement('rdf:RDF')
    rdf.setAttribute('xmlns:owl','http://www.w3.org/2002/07/owl#')
    rdf.setAttribute('xmlns:rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    rdf.setAttribute('xmlns:rdfs','http://www.w3.org/2000/01/rdf-schema#')

    ontology = xml.createElement('rdf:Ontology')
    ontology.setAttribute('rdf:about','')

    def createClass(cls):
        xcls = xml.createElement("owl:Class")
        xcls.setAttribute('rdf:about','#' + cls.__name__)
        for subclass in cls.__bases__:
            xcls.appendChild(createSubClass(subclass))
        return xcls

    def createSubClass(cls):
        xcls = xml.createElement("rdfs:subClassOf")
        xcls.setAttribute('rdf:resource','#' + cls.__name__)
        return xcls

    rdf.appendChild(ontology)

    def descend(cl):
        for cls in cl.__subclasses__():
            rdf.appendChild(createClass(cls))
            descend(cls)

    descend(icls)

    xml.appendChild(rdf)

    print xml.toprettyxml()
