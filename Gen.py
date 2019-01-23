# -*- coding: utf-8 -*-
from BEXml import BEXml
import os
experimentShortName = 'us'
outputDir = 'output'

def entryFunction(name):
    if name == '08_1a.block--drbd--drbd.ko.set' or \
        name == '32_7a.block--drbd--drbd.ko.set':
        return 'ldv_main1_sequence_infinite_withcheck_stateful'
    return 'ldv_main0_sequence_infinite_withcheck_stateful'

genXml = BEXml(
        xmlSpecification=BEXml.Specification(
            qualifiedName='benchmark',
            publicId='',
            systemId='benchmark.dtd'),
        benchmarkSetting=BEXml.Setting(
            tool='cpachecker',
            timelimit='900',
            memlimit='7000MB'),
        options=BEXml.Options(
            ('-heap','5000M'),
            #('-setprop','specification=${benchmark_path_abs}/config/specification/LDVErrorLabel.spc'),
            ('-predicateAnalysis-ABElfb',),
            # ('-entryfunction','ldv_main0_sequence_infinite_withcheck_stateful'),
            ('-disable-java-assertions',))
        )

# baseXml = BEXml.readBEXml('../bench-explicit-all.xml')

# def isInit(node):
#     name = node.getAttribute('name')
#     #assert(name is 'initial' or name is 'regression')
#     return name.split('.')[1]=='initial'
    
# def isRegr(node):
#     name = node.getAttribute('name')
#     #assert(name is 'initial' or name is 'regression')
#     return name.split('.')[1]=='regression'

# def initProcess(node):
#     treeNode = BEXml.TreeNode(node)
#     treeNode.deleteChildren(
#         customLogic=lambda x: True if x.tag is 'option' else False
#     )

#     pass

# def regrProcess(node):
#     pass

# genXml.appendCopy(base=baseXml,
#     label='rundefinition',
#     customLogic=isInit,
#     doEach=initProcess)

# genXml.appendCopy(base=baseXml,
#     label='rundefinition',
#     customLogic=isRegr,
#     doEach=regrProcess)
setName2FileName = lambda x: \
    'drivers--'+x.replace('.set','').replace('08_1a.','').replace('32_1.','').replace('32_7a.','') \
    .replace('39_7a.','').replace('43_1a.','').replace('68_1.','')
setsDir = '/media/deepin/本地磁盘/supplementary-archive/programs/sets/safeOnly'
setsFiles = os.listdir(setsDir)
for file in setsFiles:
    fileOpen = open(os.path.join(setsDir,file))
    versions = fileOpen.readlines()
    fileOpen.close()
    versions=map(lambda x:x.replace('\r','').replace('\n',''),versions)
    versions=map(os.path.basename,versions)
    setName = file
    initVersion = versions[0]
    runInit = genXml.Path().appendChild(
        BEXml.Rundefinition(experimentShortName+'.initial.'+setName)
    )
    children = runInit.appendChildren(nodes=(
            BEXml.Option(
                name='-outputpath',
                text=os.path.join('${benchmark_path_abs}',outputDir,setName,initVersion)
            ),
            BEXml.Option(
                name='-setprop',
                text='specification='+os.path.join('${benchmark_path_abs}',
                    'config','specification','LDVErrorLabel.spc')
            ),
            BEXml.Option(
                name='-stats'
            ),
            BEXml.Option(
                name='-entryfunction',
                text=entryFunction(setName)
            ),
            BEXml.Sourcefiles()
        )
    )
    children[-1].appendChild(node=(
            BEXml.CommonNode(
                label='include',
                text=os.path.join('${benchmark_path_abs}',
                    'programs',setName2FileName(setName),initVersion)
            )
        )
    )

    for index in range(1,len(versions)):
        lastVersion = versions[index-1]
        newVersion = versions[index]
        runRegression = genXml.Path().appendChild(
            BEXml.Rundefinition(experimentShortName+'.regression.'+setName+'@%d'%index)
        )
        children = runRegression.appendChildren(nodes=(
                BEXml.Option(
                name='-setprop',
                text='cpa.impacted.disj_inv=true'
                ),
                BEXml.Option(
                name='-outputpath',
                text=os.path.join('${benchmark_path_abs}',outputDir,setName,newVersion)
                ),
                BEXml.Option(
                name='-stats'
                ),
                BEXml.Option(
                name='-setprop',
                text='cpa.predicate.abstraction.initialPredicates='+
                    os.path.join('${benchmark_path_abs}',outputDir,setName,lastVersion,'predmap.txt')
                ),                
                BEXml.Option(
                name='-setprop',
                text='cpa.impacted.pre_invariants.file='+
                    os.path.join('${benchmark_path_abs}',outputDir,setName,lastVersion,'impacted-invariants.txt')
                ),
                # BEXml.Option(
                # name='-setprop',
                # text='cpa.impacted.old.file='+
                #     os.path.join('${benchmark_path_abs}',
                #         'programs',setName,lastVersion)
                # ),                
                BEXml.Option(
                name='-setprop',
                text='cpa.impacted.diff.cfaInfo='+
                    os.path.join('${benchmark_path_abs}',
                        'cfaInfo',setName,lastVersion)
                ),
                BEXml.Option(
                name='-entryfunction',
                text=entryFunction(setName)
                ),
                BEXml.Sourcefiles()
            )
        )
        children[-1].appendChild(node=(
            BEXml.CommonNode(
                label='include',
                text=os.path.join('${benchmark_path_abs}',
                    'programs',setName2FileName(setName),newVersion)
            )
        )
    )

genXml.fileOutput('out.xml')

