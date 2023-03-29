#include "helpers.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sucet = image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed;
            int priemer = sucet / 3;
            if ((sucet % 3) * 2 >= 3)
            {
                priemer += 1;
            }
            image[i][j].rgbtBlue = priemer;
            image[i][j].rgbtGreen = priemer;
            image[i][j].rgbtRed = priemer;
        }
    }
}



// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {

            int originalRed = image[i][j].rgbtRed;
            int originalGreen = image[i][j].rgbtGreen;
            int originalBlue = image[i][j].rgbtBlue;

            //using sepia algorithm on every color
            long sepiaRed = round(.393 * originalRed + .769 * originalGreen + .189 * originalBlue);
            if (sepiaRed > 255)
            {
                    sepiaRed = 255;
            }

            long sepiaGreen = round(.349 * originalRed + .686 * originalGreen + .168 * originalBlue);
            if (sepiaGreen > 255)
            {
                sepiaGreen = 255;
            }

            long sepiaBlue = round(.272 * originalRed + .534 * originalGreen + .131 * originalBlue);
            if (sepiaBlue > 255)
            {
                    sepiaBlue = 255;
            }
            
            //assigning every pixel with new color
            image[i][j].rgbtRed = sepiaRed;
            image[i][j].rgbtGreen = sepiaGreen;
            image[i][j].rgbtBlue = sepiaBlue;

        }
    }

    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE reflect[height][width];

    //fills the the new array reflect with pixels
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {

            reflect[i][width - j - 1].rgbtRed = image[i][j].rgbtRed;
            reflect[i][width - j - 1].rgbtGreen = image[i][j].rgbtGreen;
            reflect[i][width - j - 1].rgbtBlue = image[i][j].rgbtBlue;

        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //allocates memory for pointers
            int *red = malloc(sizeof(int));
            int *green = malloc(sizeof(int));
            int *blue = malloc(sizeof(int));

            //assigns pointers with the adresses of the temporary reflect array
            *red = reflect[i][j].rgbtRed;
            *green = reflect[i][j].rgbtGreen;
            *blue = reflect[i][j].rgbtBlue;

            //fills the original image with reversed pixels
            image[i][j].rgbtRed = *red;
            image[i][j].rgbtGreen = *green;
            image[i][j].rgbtBlue = *blue;

            //free the memory
            free(red);
            free(green);
            free(blue);

        }
    }

    return;
}


// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int pixelCount = 0;
            double aroundSumRed = 0;
            double aroundSumGreen = 0;
            double aroundSumBlue = 0;
            double boxAvrgRed;
            double boxAvrgGreen;
            double boxAvrgBlue;

            //neighboring pixels
            for (int k = 1; k >= -1; k--)
            {
                for (int l = 1; l >= -1; l--)
                {

                    //helping variables to check the borders
                    int a = i - k;
                    int b = j - l;

                    //checks if the pixel is not outside the image
                    if (((a >= 0) && (a < height)) && ((b >= 0) && (b < width)))
                    {

                        aroundSumRed = aroundSumRed + image[a][b].rgbtRed;
                        aroundSumGreen = aroundSumGreen + image[a][b].rgbtGreen;
                        aroundSumBlue = aroundSumBlue + image[a][b].rgbtBlue;
                        pixelCount++;

                    }
                }

            }

            //average values for each color
            boxAvrgRed = roundf(aroundSumRed / pixelCount);
            boxAvrgGreen = roundf(aroundSumGreen / pixelCount);
            boxAvrgBlue = roundf(aroundSumBlue / pixelCount);

            //filling the pixel with the average value
            image[i][j].rgbtBlue = boxAvrgBlue;
            image[i][j].rgbtGreen = boxAvrgGreen;
            image[i][j].rgbtRed = boxAvrgRed;
        }

    }

    return;
}
