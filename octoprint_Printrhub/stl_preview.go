package main
import (
       .
       "github.com/fogleman/fauxgl"
       "github.com/nfnt/resize"
       "flag"
)

const (
      scale	= 1
      width 	= 540
      height 	= 480
      fovy	= 30	// vertical field of view degrees
      near	= 1  	// near clipping plane
      far	= 10 	// far cliping plane
)

var   (
      eye	= V(-3, 1, 0.75)		// camera position
      center	= V(0, -0.07, 0)	   	// view center position
      up	= V(0, 1, 0)  		   	// up vector
      light 	= V(-0.75, 1, 0.25).Normalize()	// light direction
)

func main () {

     	inputFile  := flag.String("input", "", "STL file to render")
     	outputFile := flag.String("output", "out.png", "output PNG file")
     	colorVal   := flag.String("color", "#468966", "Base color for object")

     	flag.Parse()

	// load a mesh
     	mesh, err := LoadSTL(*inputFile)
        if err != nil {
     	    panic(err)
	}

	// fit mesh in a bi-unit cube centered at the origin
	mesh.BiUnitCube()

	// smooth the normals
	mesh.SmoothNormalsThreshold(Radians(30))

	// create a rendering context
	context := NewContext(width*scale, height*scale)
	context.ClearColorBufferWith(HexColor("#FFF8E3"))

	// create transformation matrix and light direction
	aspect := float64(width) / float64(height)
	matrix := LookAt(eye, center, up).Perspective(fovy, aspect, near, far)

	// use builtin phong shader
	shader := NewPhongShader(matrix, light, eye)
	shader.ObjectColor = HexColor(*colorVal)
	context.Shader = shader

	// render
	context.DrawMesh(mesh)

	// downsample image for antialiasing
	image := context.Image()
	image = resize.Resize(width, height, image, resize.Bilinear)

	// save image
	SavePNG(*outputFile, image)
}
