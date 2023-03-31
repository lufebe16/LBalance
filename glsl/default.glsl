/* default.glsl

  default used in kivy assembled from header.* and default.* files.
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute vec3     vPosition;
attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;
uniform float      opacity;

void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform mat4 frag_modelview_mat;

void main (void){
    gl_FragColor = frag_color * texture2D(texture0, tex_coord0);
}
