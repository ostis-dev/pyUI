import distutils.sysconfig
import distutils.core
import os, shutil, sys, glob
import py2exe

script_dir = os.path.dirname(os.path.abspath(__file__))

include_mods = []
include_packs = []
data_files = []

bin_dist_path = os.path.join(script_dir, "bin\\dist")

def runtime_libraries_find():
    
    print "Trying to find microsoft runtime libraries"
    
    dep_path = os.path.join(script_dir, 'dep')
    
    #if not os.path.isdir(dep_path):
    #    os.makedirs(dep_path)
        
    # trying to find need runtime libraries
    runtime_search_paths = ['C:\\Program Files\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT\\',
                            'C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT\\']
    runtime_path = None
    for path in runtime_search_paths:
        if os.path.isdir(path):
            runtime_path = path
            break
            
    print "Microsoft runtime path: %s" % str(runtime_path)
            
    # copy runtime libraries if we have founded it
    if runtime_path is not None:
        sys.path.append(runtime_path)
        #names = os.listdir(runtime_path)
        #for name in names:
        #    shutil.copy2(os.path.join(runtime_path, name),
        #                os.path.join(dep_path, name))
   
    # trying to find ogre runtime libraries
    print "Trying to find ogre runtime libraries"

    python_lib_path = distutils.sysconfig.get_python_lib()
    ogre_path = os.path.join(python_lib_path, "ogre")
    
    # get renderer path
    ogre_renderer_path = os.path.join(ogre_path, "renderer\\OGRE")
    if os.path.isdir(ogre_renderer_path):
        sys.path.append(ogre_renderer_path)

    # mygui path
    mygui_path = os.path.join(python_lib_path, "suit\\core\\render\\mygui")
    if os.path.isdir(mygui_path):
        sys.path.append(mygui_path)
        
    # append path to syspath
    sys.path.append(dep_path)
        
        
def prepare_include_modules():
    
    print "Prepare modules for include"
    
    sys.path.append(os.path.join(script_dir, "..\\repo"))
    include_mods.append("repoBuilder")
    #sys.path.append(os.path.join(script_dir, "..\\"))
    #include_mods.append("components")
    
    #comp_path = os.path.join(script_dir, "..\\components")
    #comps = os.listdir(comp_path)
    #for c in comps:
    #    path = os.path.join(comp_path, c)
    #    if len(c) == 0 or c.startswith(".") or not os.path.isdir(path):
    #        continue
    #    sys.path.append(path)
    #    include_mods.append("components." + str(c))
    
    
    #include_mods.append("components.audio")
    
def prepare_packages():
    
    print "Prepare packages"
    
    sys.path.append(os.path.join(script_dir, "..\\"))
    include_packs.append("components")
    include_packs.append("operations")
    
def prepare_plugins():

    print "Prepare plugins"

    shutil.copytree(os.path.normpath("..\\plugins"),
                os.path.join(bin_dist_path, "plugins"),
                ignore = shutil.ignore_patterns(".svn*"))
    
    shutil.copy2(os.path.join(script_dir, "../plugins.cfg"), os.path.join(bin_dist_path, "plugins.cfg"))
                
def prepare_media():

    print "Prepare media"

    shutil.copytree(os.path.normpath("..\\media"),
                os.path.join(bin_dist_path, "media"),
                ignore = shutil.ignore_patterns(".svn*"))
                
                
    shutil.copy2(os.path.join(script_dir, "../resources.cfg"), os.path.join(bin_dist_path, "resources.cfg"))
    
def prepare_fs_repo():
    
    print "Parepare fs_repo"        
    #data_files.append(("fs_repo_src", glob.glob(os.path.join("..\\repo\\fs_repo_src\\*"))))
    #data_files.append()
    
    #for (root, dirs, files) in os.walk(os.path.normpath("..\\repo\\fs_repo_src\\")):
    shutil.copytree(os.path.normpath("..\\repo\\fs_repo_src\\"),
                    os.path.join(bin_dist_path, "fs_repo_src"),
                    ignore = shutil.ignore_patterns(".svn*"))
    
    #print data_files
    
def prepare_tools():
    
    print "Prepare binary tools"
    
    shutil.copytree(os.path.normpath("..\\repo\\repoBuilder\\bin"),
                    os.path.join(bin_dist_path, "bin"),
                    ignore = shutil.ignore_patterns(".svn*"))
                    
def prepare_configs():
    print "Prepare configs"
    shutil.copy2(os.path.join(".", "wiki2sc.conf.example"), os.path.join(bin_dist_path, "wiki2sc.conf"))
    
def prepare_scripts():
    
    print "Prepare scripts"
    copy_list = ['start.bat', 'rebuild.bat', 'start_rebuild.bat']
    
    for ci in copy_list:
        shutil.copy2(os.path.join(".", ci), os.path.join(bin_dist_path, ci))
        
    # copy build rules
    shutil.copy2(os.path.join(script_dir, "../repo/build.rules"), os.path.join(bin_dist_path, "build.rules"))
    

if os.path.isdir("./bin"):
    shutil.rmtree("./bin")
if os.path.isdir("./build"):
    shutil.rmtree("./build")
    
# find runtime libraries
runtime_libraries_find()

# prepare modules for include
prepare_include_modules()
# prepare packages
prepare_packages()
   
#os.chdir('..')

distutils.core.setup(
        console=['../start.py', '../repo/rule_builder.py'],
        options={
                "py2exe": {
                    "optimize" : 0,
                    "dist_dir" : 'bin/dist',
                    "includes" : include_mods,
                    "compressed" : 0,
                    "packages" : include_packs
                }
        },
        data_files = data_files
)

prepare_fs_repo()
prepare_scripts()
prepare_configs()
prepare_tools()
prepare_plugins()
prepare_media()