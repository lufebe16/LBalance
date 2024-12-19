/* default.glsl

  simple diffuse lighting based on laberts cosine law; see e.g.:
    http://en.wikipedia.org/wiki/Lambertian_reflectance
    http://en.wikipedia.org/wiki/Lambert%27s_cosine_law
  
  derived from default.glsl integrating step by step simple.glsl from
  the kivy 3d-monkey-example. (simple.glsl did work on desktop but
  not on android!) /LB
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;
varying vec4 normal_vec;
varying vec4 vertex_pos;

/* vertex attributes */
attribute vec3     vPosition;
attribute vec2     vTexCoords0;
attribute vec3     v_normal;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;
uniform float      opacity;

void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  vec4 pos = modelview_mat * vec4(vPosition,1.0);
  vertex_pos = pos;
  normal_vec = vec4(v_normal,0.0);
  gl_Position = projection_mat * pos;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;
varying vec4 normal_vec;
varying vec4 vertex_pos;

/* uniform texture samplers */
uniform sampler2D texture0;

uniform mat4 frag_modelview_mat;
uniform mat4 normal_mat;

void main (void){
    /* correct normal, and compute light vector (assume light at the eye) */
    vec4 v_norm = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );
    /* reflectance based on lamberts law of cosine */
    float theta = clamp(dot(v_norm, v_light), 0.0, 1.0);
    
    /* must use the sampler2D on android (ES 2.0 ?) otherwise crashes */
    /* (on desktop works without !) */
    vec4 fcol = frag_color * texture2D(texture0, tex_coord0);
    gl_FragColor = fcol * vec4(theta, theta, theta, 1.0);
}
