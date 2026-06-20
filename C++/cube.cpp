#include <GL/glut.h>

// Function to draw the cube
void display() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();

    // Rotate the cube so we can see it's 3D
    glRotatef(45, 1.0, 1.0, 0.0); 

    glBegin(GL_QUADS);
        // Front Face (Red)
        glColor3f(1.0, 0.0, 0.0);
        glVertex3f(-0.5, -0.5,  0.5);
        glVertex3f( 0.5, -0.5,  0.5);
        glVertex3f( 0.5,  0.5,  0.5);
        glVertex3f(-0.5,  0.5,  0.5);

        // Back Face (Green)
        glColor3f(0.0, 1.0, 0.0);
        glVertex3f(-0.5, -0.5, -0.5);
        glVertex3f(-0.5,  0.5, -0.5);
        glVertex3f( 0.5,  0.5, -0.5);
        glVertex3f( 0.5, -0.5, -0.5);

        // Top Face (Blue)
        glColor3f(0.0, 0.0, 1.0);
        glVertex3f(-0.5,  0.5, -0.5);
        glVertex3f(-0.5,  0.5,  0.5);
        glVertex3f( 0.5,  0.5,  0.5);
        glVertex3f( 0.5,  0.5, -0.5);

        // Bottom Face (Yellow)
        glColor3f(1.0, 1.0, 0.0);
        glVertex3f(-0.5, -0.5, -0.5);
        glVertex3f( 0.5, -0.5, -0.5);
        glVertex3f( 0.5, -0.5,  0.5);
        glVertex3f(-0.5, -0.5,  0.5);
    glEnd();

    glFlush();
    glutSwapBuffers();
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutCreateWindow("C++ 3D Cube");
    glEnable(GL_DEPTH_TEST);
    glutDisplayFunc(display);
    glutMainLoop();
    return 0;
}