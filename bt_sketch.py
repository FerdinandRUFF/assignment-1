# Import javascript modules
from js import THREE, window, document, Object
# Import pyscript / pyodide modules
from pyodide.ffi import create_proxy, to_js
# Import python module
import math

#-----------------------------------------------------------------------
# USE THIS FUNCTION TO WRITE THE MAIN PROGRAM
def main():
    #-----------------------------------------------------------------------
    # VISUAL SETUP
    # Declare the variables
    global renderer, scene, camera, controls,composer
    
    #Set up the renderer
    renderer = THREE.WebGLRenderer.new()
    renderer.setPixelRatio( window.devicePixelRatio )
    renderer.setSize(window.innerWidth, window.innerHeight)
    document.body.appendChild(renderer.domElement)

    # Set up the scene
    scene = THREE.Scene.new()
    back_color = THREE.Color.new(0.1,0.1,5)
    scene.background = back_color
    camera = THREE.PerspectiveCamera.new(75, window.innerWidth/window.innerHeight, 0.1, 1000)
    camera.position.z = 50
    scene.add(camera)

    # Graphic Post Processing
    global composer
    post_process()

    # Set up responsive window
    resize_proxy = create_proxy(on_window_resize)
    window.addEventListener('resize', resize_proxy) 
    #-----------------------------------------------------------------------
    # YOUR DESIGN / GEOMETRY GENERATION
    # Geometry Creation
    global geom_params, cube, cube_lines, cylinders_x, cylinders_y, cylinder_lines
    cubes = []
    cube_lines = []
    # zwei weitere leere Listen anlegen
    cylinders_x = []
    cylinders_y = []
    cylinder_lines = []

    geom_params_cylinder = {
        "radius_top_and_bottom": 5,
        "height": 20,
        "radial_segments": 32,
        "x": 2,
        "y": 2,
        "rotation_x": 45,
        "rotation_y": 0,
        "type": "cylinder"
    }
    geom_params_cube = {
        "size": 30,
        "x": 2,
        "rotation": 45,
        "type": "cube"
    }

    # auskommentieren, je nachdem welches objekt wir wollen
    geom_params = geom_params_cylinder
    #geom_params = geom_params_cube

    geom_params = Object.fromEntries(to_js(geom_params))

    # create materials 
    global material, line_material 
    color = THREE.Color.new(255,255,255)
    material = THREE.MeshBasicMaterial.new()
    material.transparent = True
    material.opacity = 0.01

    line_material = THREE.LineBasicMaterial.new()
    line_material.color = color

    if geom_params.type == "cube":
        # Generate the boxes using for loop
        for i in range (geom_params.x):
            # erstellt Außenmaße unserer Würfel,new braucht 2 werte um zu arbeiten
            geom = THREE.BoxGeometry.new(geom_params.size, geom_params.size)

            geom.translate (geom_params.size*i,0,0)
            geom.rotateX(math.radians(geom_params.rotation)/geom_params.x*i)

            cube = THREE.Mesh.new(geom, material)
            cubes.append(cube)
            scene.add(cube)

            #draw the cube lines
            edges = THREE.EdgesGeometry.new(cube.geometry)
            line = THREE.LineSegments.new(edges,line_material)
            cube_lines.append(line)
            scene.add(line)

    elif geom_params.type == "cylinder":
        # Generate the boxes using for loop
        for i in range (geom_params.x):
            geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom, geom_params.height, geom_params.radial_segments)

            geom.translate(geom_params.radius_top_and_bottom*i*2,0,0)
            geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)

            cylinder = THREE.Mesh.new(geom, material)
            cylinders_x.append(cylinder)
            scene.add(cylinder)

            #draw the cylinder lines
            edges = THREE.EdgesGeometry.new(cylinder.geometry)
            line = THREE.LineSegments.new(edges,line_material)
            cylinder_lines.append(line)
            scene.add(line)
            # extend to second lane
            for j in range (geom_params.y):
                #geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom, geom_params.height, geom_params.radial_segments)

                geom.translate(0, 0, geom_params.radius_top_and_bottom*2)
                geom.rotateX(math.radians(geom_params.rotation_y)/geom_params.y*j)

                cylinder = THREE.Mesh.new(geom, material)
                cylinders_y.append(cylinder)
                scene.add(cylinder)

                # draw the cylinder lines
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                cylinder_lines.append(line)
                scene.add(line)




    #-----------------------------------------------------------------------
    # USER INTERFACE
    # Set up Mouse orbit control
    controls = THREE.OrbitControls.new(camera, renderer.domElement)

    # Set up GUI
    gui = window.dat.GUI.new()
    param_folder = gui.addFolder('Parameters')
    # hier stellen wir ein, was der user an den würfeln verändern kann.
    param_folder.add(geom_params, 'radius_top_and_bottom', 5, 100, 1)
    param_folder.add(geom_params, 'x', 2, 10, 1)
    param_folder.add(geom_params, 'y', 2, 10, 1)
    param_folder.add(geom_params, 'rotation_x', 0, 270)
    #param_folder.add(geom_params, 'rotation_y', 0, 270)
    param_folder.open()
    
    #-----------------------------------------------------------------------
    # RENDER + UPDATE THE SCENE AND GEOMETRIES
    render()
    
#-----------------------------------------------------------------------
# HELPER FUNCTIONS
#update the cubes 
def update_cubes ():
    global cubes, cube_lines, material, line_material
    #make sure you dont have 0 cubes 

    if len(cubes) != 0:
        if len(cubes) != geom_params.x:
            # alle vorhandenen cubes löschen
            for cube in cubes: 
                scene.remove(cube)
            # alle vorhandenen lines löschen
            for line in cube_lines: 
                scene.remove(line)
            
            cubes = []
            cube_lines = []

            for i in range (geom_params.x):
                # setze den würfel in die GUI rein
                geom = THREE.BoxGeometry.new(geom_params.size,geom_params.size)
                geom.translate (geom_params.size*i,0,0)
                geom.rotateX(math.radians(geom_params.rotation)/geom_params.x*i)
                # erstelle würfel
                cube = THREE.Mesh.new(geom, material)
                cubes.append(cube)
                scene.add(cube)

                #draw the cube lines
                edges = THREE.EdgesGeometry.new(cube.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                cube_lines.append(line)
                # setze den würfel in die scene
                scene.add(line)
        else:
            for i in range (len(cubes)):
                cube = cubes[i]
                line = cube_lines[i]
                # setze den würfel in die GUI rein - sind schon da, werden nur neu ausgerichtet
                geom = THREE.BoxGeometry.new(geom_params.size,geom_params.size,geom_params.size)
                geom.translate (geom_params.size*i,0,0)
                geom.rotateX(math.radians(geom_params.rotation)/geom_params.x*i)

                cube.geometry = geom
                
                edges = THREE.EdgesGeometry.new(cube.geometry)
                line.geometry = edges



#update the cylinders 
def update_cylinders():
    global cylinders_x, cylinders_y, cylinder_lines, material, line_material

    #make sure you dont have 0 cylinders
    if len(cylinders_x) != 0 or len(cylinders_y) != 0:
        if len(cylinders_x) != geom_params.x and len(cylinders_y) != geom_params.y:
            # alle vorhandenen cubes löschen
            for cylinder in cylinders_x:
                scene.remove(cylinder)
            for cylinder in cylinders_y:
                scene.remove(cylinder)
            # alle vorhandenen lines löschen
            for line in cylinder_lines: 
                scene.remove(line)
            
            # cylinders_x = []
            # cylinders_y = []
            # cylinder_lines = []

            for i in range (geom_params.x):
                # setze den zylinder in die GUI rein
                geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom, geom_params.height, geom_params.radial_segments)
                geom.translate (geom_params.radius_top_and_bottom*i*2,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
                # erstelle Zylinder
                cylinder = THREE.Mesh.new(geom, material)
                cylinders_x.append(cylinder)
                scene.add(cylinder)

                #draw the cylinder lines
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line = THREE.LineSegments.new(edges,line_material)
                cylinder_lines.append(line)
                # setze den cylinder in die scene
                scene.add(line)
                for j in range(geom_params.y):
                    #geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom,
                    #                                  geom_params.height, geom_params.radial_segments)

                    geom.translate(0, 0, geom_params.radius_top_and_bottom * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.x * j)

                    cylinder = THREE.Mesh.new(geom, material)
                    cylinders_y.append(cylinder)
                    scene.add(cylinder)

                    # draw the cylinder lines
                    edges = THREE.EdgesGeometry.new(cylinder.geometry)
                    line = THREE.LineSegments.new(edges, line_material)
                    cylinder_lines.append(line)
                    scene.add(line)
        else:
            for i in range (len(cylinders_x)):
                cylinder = cylinders_x[i]
                line = cylinder_lines[i]
                # setze den würfel in die GUI rein - sind schon da, werden nur neu ausgerichtet
                geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom, geom_params.height, geom_params.radial_segments)
                geom.translate (geom_params.radius_top_and_bottom*i*2,0,0)
                geom.rotateX(math.radians(geom_params.rotation_x)/geom_params.x*i)
    
                cylinder.geometry = geom
    
                edges = THREE.EdgesGeometry.new(cylinder.geometry)
                line.geometry = edges
                for j in range(len(cylinders_y)):
                    cylinder = cylinders_y[j]
                    line = cylinder_lines[len(cylinders_x)+j]
                    # setze den würfel in die GUI rein - sind schon da, werden nur neu ausgerichtet
                    geom = THREE.CylinderGeometry.new(geom_params.radius_top_and_bottom, geom_params.radius_top_and_bottom,
                                                    geom_params.height, geom_params.radial_segments)
                    geom.translate(0,0, geom_params.radius_top_and_bottom * 2)
                    geom.rotateX(math.radians(geom_params.rotation_y) / geom_params.y * j)

                    cylinder.geometry = geom

                    edges = THREE.EdgesGeometry.new(cylinder.geometry)
                    line.geometry = edges
                



# Simple render and animate
def render(*args):
    window.requestAnimationFrame(create_proxy(render))
    update_cylinders()
    #update_cubes()
    controls.update()
    composer.render()

# Graphical post-processing
def post_process():
    render_pass = THREE.RenderPass.new(scene, camera)
    render_pass.clearColor = THREE.Color.new(0,0,0)
    render_pass.ClearAlpha = 0
    fxaa_pass = THREE.ShaderPass.new(THREE.FXAAShader)

    pixelRatio = window.devicePixelRatio

    fxaa_pass.material.uniforms.resolution.value.x = 1 / ( window.innerWidth * pixelRatio )
    fxaa_pass.material.uniforms.resolution.value.y = 1 / ( window.innerHeight * pixelRatio )
   
    global composer
    composer = THREE.EffectComposer.new(renderer)
    composer.addPass(render_pass)
    composer.addPass(fxaa_pass)

# Adjust display when window size changes
def on_window_resize(event):

    event.preventDefault()

    global renderer
    global camera
    
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    #post processing after resize
    post_process()
#-----------------------------------------------------------------------
#RUN THE MAIN PROGRAM
if __name__=='__main__':
    main()

    #homework: boxen vermehren sich in zwei richtungen und andere Geometrien ausprobieren mit dem Link auf ilias 
    

    #homework: boxen vermehren sich in zwei richtungen und andere Geometrien ausprobieren mit dem Link auf ilias 
    