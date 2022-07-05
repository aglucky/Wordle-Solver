# WordleSolver

This project uses Tesseact and OpenCV to take a screenshot of a wordle game and provide a list of up to five of the "best" (aka most distinct characters) guesses. 
To use, take a screenshot of the wordle game, place it into the project directory and rename it to "wordle.png". Then, run the script to get a list of the best guesses.

## Notes

- Take a screenshot of only the grid for the best results
- The error and size variables in the filterContour loop may need to be adjsted per run

## Todo

- [ ] Normalize images so resolution doesn't affect results
- [ ] Add more error handling for when empty boxes are processed
- [ ] Add commandline support for easier deployment
- [ ] Add to telegram bot
  - Figure out how to use Tesseract in Azure App Services or switch to Azure OCR
  
