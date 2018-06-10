package main

// This file was updated with settings that match the values
// oddirmeyer used in Printrbot Cloud... but there's no automated
// process to keep these in sync right now. 

import (
       .
       "github.com/fogleman/fauxgl"
       "github.com/nfnt/resize"
       "flag"
)

const (
      scale		  = 4
      near		  = 1  	// near clipping plane
      far	    	  = 10 	// far cliping plane
      defaultFovy   	  = 40.0
      defaultWidth 	  = 540
      defaultHeight 	  = 480
      defaultWorldColor	  = "E0D9CC"
      defaultObjectColor  = "F09500" 
)

var   (
      eye	= V(3, 1, 1.75)			// camera position
      center	= V(0, 0, 0)			// view center position
      up	= V(0, 0, 1)  		   	// up vector
      light 	= V(-0.75, 1, 0.25).Normalize()	// light direction
)

func main () {

     	inputFile  := flag.String("input", "", "STL file to render")
     	outputFile := flag.String("output", "out.png", "output PNG file")
     	colorVal   := flag.String("color", defaultObjectColor,
		      	          "Base color for object")

     	flag.Parse()

	// load a mesh
     	mesh, err := LoadSTL(*inputFile)
        if err != nil {
     	    panic(err)
	}

	// fit mesh in a bi-unit cube centered at the origin
	mesh.BiUnitCube()
	// rotate on z-axis
	mesh.Transform(Rotate(V(0, 0, 1.0), Radians(-90)))
	// smooth the normals
	//mesh.SmoothNormalsThreshold(Radians(30))

	// create a rendering context
	context := NewContext(defaultWidth*scale, defaultHeight*scale)
	context.ClearColorBufferWith(HexColor(defaultWorldColor))

	// create transformation matrix and light direction
	aspect := float64(defaultWidth) / float64(defaultHeight)
	matrix := LookAt(eye, center, up).Perspective(defaultFovy, aspect,
						      near, far)
        light := V(3.5, 1, 1.5).Normalize()

	// use builtin phong shader
	shader := NewPhongShader(matrix, light, eye)
	shader.ObjectColor = HexColor(*colorVal)
	shader.DiffuseColor = Gray(0.8)
	shader.SpecularColor = Gray(0.55)
	shader.SpecularPower = 90
	context.Shader = shader

	// render
	context.DrawMesh(mesh)

	// downsample image for antialiasing
	image := context.Image()
	image = resize.Resize(defaultWidth, defaultHeight, image,
	                      resize.Bilinear)

	// save image
	SavePNG(*outputFile, image)
}
