#include <GL/glut.h>
#include <string>
#include <iostream>

float result = 0;
std::string display_text = "Result: 0";

// Function to render text on the screen
void drawText(const char* text, int x, int y) {
    glRasterPos2i(x, y);
    while (*text) {
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, *text);
        text++;
    }
}

void display() {
    glClear(GL_COLOR_BUFFER_BIT);
    glColor3f(1.0, 1.0, 1.0); // White text
    
    drawText("--- OpenGL Calculator ---", 120, 250);
    drawText(display_text.c_str(), 150, 150);
    drawText("Enter operation in Terminal (e.g., 5 + 3)", 80, 50);
    
    glutSwapBuffers();
}

void performCalculation() {
    float a, b;
    char op;
    std::cout << "\nEnter calculation (Num1 Operator Num2): ";
    if (std::cin >> a >> op >> b) {
        switch(op) {
            case '+': result = a + b; break;
            case '-': result = a - b; break;
            case '*': result = a * b; break;
            case '/': result = (b != 0) ? a / b : 0; break;
            default: std::cout << "Invalid Operator!"; return;
        }
        display_text = "Result: " + std::to_string(result);
        glutPostRedisplay(); // Refresh the OpenGL window
    }
}

int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowSize(500, 300);
    glutCreateWindow("C++ Graphic Calculator");
    
    gluOrtho2D(0, 500, 0, 300); // Set 2D coordinate system
    
    glutDisplayFunc(display);
    glutIdleFunc(performCalculation); // Keeps asking for input
    
    glutMainLoop();
    return 0;
}