# -*- coding: utf-8 -*-
from xml.dom import minidom

class BEXml:
    '''
    Args:
        xmlSpecification
        benchmarkSetting
        options
        [TODO] other args if needed
    '''
    
    def __init__(self,xmlSpecification=None,benchmarkSetting=None,**globalSettings):
        impl=minidom.DOMImplementation()
        if xmlSpecification is not None:
            #self.xmlSpecification=xmlSpecification
            doctype=impl.createDocumentType(
                qualifiedName=xmlSpecification.qualifiedName,
                publicId=xmlSpecification.publicId,
                systemId=xmlSpecification.systemId
            )
        else: # benchexec default Xml specification
            doctype=impl.createDocumentType(
                qualifiedName='benchmark',
                publicId='+//IDN sosy-lab.org//DTD BenchExec benchmark 1.17//EN',
                systemId='https://www.sosy-lab.org/benchexec/benchmark-1.17.dtd'
            )
        doc=impl.createDocument(None,'benchmark',doctype)
        self.doc=doc
        if benchmarkSetting is not None:
            root=self.doc.documentElement
            map(lambda x:None if x[1] is None else root.setAttribute(x[0],x[1]),
                benchmarkSetting.settings)
        options=globalSettings.get('options')
        if options is not None:
            for item in options:
                self.doc.documentElement.appendChild(item)
             
    @staticmethod
    def Options(*options):
        doc=minidom.Document()
        OptList=[]
        for option in options:
            OptNode=doc.createElement('option')
            OptNode.setAttribute('name',option[0])
            if len(option)>1:
                text=doc.createTextNode(option[1])
                OptNode.appendChild(text)
            OptList.append(OptNode)
        return OptList


    @staticmethod
    def Option(name,text=None):
        doc=minidom.Document()
        OptNode=doc.createElement('option')
        OptNode.setAttribute('name',name)
        if text is not None:
            textNode=doc.createTextNode(text)
            OptNode.appendChild(textNode)
        return OptNode


    @staticmethod
    def Rundefinitions(*rundefinitions):
        # TODO:
        raise NotImplementedError
        

    @staticmethod
    def Rundefinition(name):
        doc=minidom.Document()
        RunNode=doc.createElement('rundefinition')
        RunNode.setAttribute('name',name)
        return RunNode


    @staticmethod
    def Tasks():
        '''Tasks also called: sourcefiles
        '''
        return BEXml.Sourcefiles()

    @staticmethod
    def Sourcefiles():
        doc=minidom.Document()
        SouNode=doc.createElement('sourcefiles')
        return SouNode

    @staticmethod
    def CommonNodes(*commonNodes):
        doc=minidom.Document()
        NodeList=[]
        for commonNode in commonNodes:
            Node=doc.createElement(commonNode[0]) # Node tag
            attributes=[]
            text=None
            if len(commonNode)>1:
                if type(commonNode[1]) is type(''):
                    text = commonNode[1]
                elif type(commonNode[1]) is type([]):
                    attributes = commonNode[1]
            if len(commonNode)>2:
                if type(commonNode[2]) is type(''):
                    text = commonNode[2]
                elif type(commonNode[2]) is type([]):
                    attributes = commonNode[2]
            for attr in attributes:
                Node.setAttribute(attr[0],attr[1])
            if text is not None:
                Node.appendChild(doc.createTextNode(text))
            NodeList.append(Node)
        return NodeList


    @staticmethod
    def CommonNode(label,attributes=[],text=None):
        doc=minidom.Document()      
        Node=doc.createElement(label) # Node tag
        for attr in attributes:
            Node.setAttribute(attr[0],attr[1])
        if text is not None:
            Node.appendChild(doc.createTextNode(text))
        return Node
        

    # @staticmethod
    # def Option(name,value=None):
    #     doc=minidom.Document()
    #     OptNode=doc.createElement('option')
    #     OptNode.setAttribute('name',name)
    #     if value is not None:
    #         text=doc.createTextNode(value)
    #         OptNode.appendChild(text)
    #     return OptNode

    # def append(self,path=[],obj=[],doEach=lambda x:None):
    #     '''
    #     '''
    #     root = self.doc.documentElement
    #     for level in path:
 
    #         elements=root.getElementsByTagName(level[0])
    #         rootFind = False
    #         if len(level)==1:
    #             if len(elements)==1:
    #                 root = elements[0]
    #                 rootFind = True
    #         else:
    #             for element in elements:
    #                 if element.hasAttribute(level[1][0])==level[1][1]:
    #                     root = element
    #                     rootFind = True
    #                     break
    #         if rootFind is False:
    #             return False
    #     for item in obj:
    #         root.appendChild(item)
    #         doEach(item)
    #     return True
        

    def appendCopy(self,base,label,path=[],
            customLogic=lambda x:True,doEach=lambda x:None):
        '''Copy specific nodes from another XML

        Copy the nodes with the given label under the given path. You can
        using a custom logic to access a finer specification. After each
        copy a given function will be done if needed. Notes path must exist
        both in self and base xml.(first if multi-choice)

        Args:
            base: XML that copy from
            label: node label to copy
            path: path to the label to copy
                path = [(tagName,feature),...]
                where: feature = (attribute,value) [TODO: List needed?]
                default path value is [] that means under tag 'benchmark'
            customLogic: define choose or not, default to always choose
            doEach: operation to each node after copy, default do nothing
        
        Returns:
            Success: True
            Failed: False
        '''
        root = self.Path(path)
        rootBase = base.Path(path)
        if root is None or rootBase is None:
            return False
        
        appendList=rootBase.getElementsByTagName(label)
        for item in appendList:
            if customLogic(item):
                root.node.appendChild(item)
                doEach(item)
        return True

    @staticmethod
    def readBEXml(filename):
        doc=minidom.parse(filename)
        # print doc
        beXml = BEXml()
        beXml.doc = doc
        return beXml
    
    def stdOutput(self,Kind='Pretty'):
        print self.doc.toprettyxml() if Kind=='Pretty' else self.doc.toxml()
    def fileOutput(self,filename,Kind='Pretty'):
        f=open(filename,'w')
        f.write(self.doc.toprettyxml() if Kind=='Pretty' else self.doc.toxml())
        f.close()

    def Path(self,path=[]):
        root = self.doc.documentElement
        for level in path:
            elements=root.getElementsByTagName(level[0])
            rootFind = False

            if len(level)==1:
                if len(elements)==1:
                    root = elements[0]
                    rootFind = True
            else:
                for element in elements:
                    if element.hasAttribute(level[1][0])==level[1][1]:
                        root = element
                        rootFind = True
                        break
            if not rootFind:
                return None
        return BEXml.TreeNode(root)


    class TreeNode:
        def __init__(self,node):
            self.node=node
        def appendChildren(self,nodes=(),customLogic=lambda x:True,doEach=lambda x:None):
            for node in nodes:
                if customLogic(node):
                    self.node.appendChild(node)
                    doEach(node)
            return map(BEXml.TreeNode,nodes)
        def appendChild(self,node,customLogic=lambda x:True,doEach=lambda x:None):
            if customLogic(node):
                self.node.appendChild(node)
                doEach(node)
            return BEXml.TreeNode(node)
        def deleteChildren(self,customLogic=lambda x:True,kind='all'):
            for node in self.node.childNodes:
                if customLogic(node):
                    self.node.removeChild(node)
                    if kind=='first':
                        break


    class Specification:
        def __init__(self,qualifiedName='benchmark',publicId='',systemId='benchmark.dtd'):
            self.qualifiedName=qualifiedName
            self.publicId=publicId
            self.systemId=systemId


    class Setting:
        def __init__(self,tool=None,timelimit=None,walltimelimit=None,
            hardtimelimit=None,memlimit=None,cpuCores=None,threads=None):
            self.settings=[]
            self.settings.append(('tool',tool))
            self.settings.append(('timelimit',timelimit))
            self.settings.append(('walltimelimit',walltimelimit))
            self.settings.append(('hardtimelimit',hardtimelimit))
            self.settings.append(('memlimit',memlimit))
            self.settings.append(('cpuCores',cpuCores))
            self.settings.append(('threads',threads))


if __name__ == "__main__":
    
    o = BEXml.readBEXml(u'/media/deepin/本地磁盘/supplementary-archive/XmlGen/copy.xml')
    # o.stdOutput(Kind='Normal')

    x = BEXml(
        xmlSpecification=BEXml.Specification(
            qualifiedName='benchmark',
            publicId='',
            systemId='benchmark.dtd'),
        benchmarkSetting=BEXml.Setting(
            tool='cpachecker',
            timelimit='900',
            memlimit='7000'),
        options=BEXml.Options(
            ('-heap','5000M'))
            )
    # x.appendCopy(o,'rundefinition')
    x.Path().appendChild(
        BEXml.Option(
                name='-setprop',
                text='specification=${benchmark_path_abs}/LDVErrorLabel.spc'
                )
            )
    run1 = x.Path().appendChild(
        BEXml.Rundefinition('pa.initial.08_1a.auxdisplay--cfag12864b.ko')            
        )
    run1.appendChild(
        BEXml.Option(
                name='-setprop',
                text='analysis.entryFunction=ldv_main0_sequence_infinite_withcheck_stateful'
                )        
            )
    sou1 = run1.appendChild(
        BEXml.Sourcefiles() 
        )
    sou1.appendChildren(nodes=(
            BEXml.CommonNode(
                label='includesfile',
                text='${benchmark_path_abs}/programs/sets/safeOnly/08_1a.auxdisplay--cfag12864b.ko.set'
                ),
            BEXml.Option(
                name='-64'
                )
            )
        )
    # x.append(
    #     obj=BEXml.Options(
    #         ('-setprop','specification=${benchmark_path_abs}/LDVErrorLabel.spc'))
    #     )
    x.stdOutput()
    # x.fileOutput('out.xml',Kind='Normal')
    pass