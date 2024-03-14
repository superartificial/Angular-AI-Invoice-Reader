# Frontend

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 17.2.3.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.


I have a large text file, containing many pages of code, which I need to compress. It needs to stay in a text based format, and the output contents needs to be easily interpretable by a LLM. Can you write me a Python script to do this?

Here is a python script that recursively concatenates contents of a directory, ignoring those defined in .gitignore files. 
Please help me update it so that the output file name includes a number suffix, and if the output file size exceeds 75kb start a new one for the next input file, with the number incremented. 