# E-library

Welcome to the **E-library** project! This small web-application allows users to upload, and explore books.

## Features

- **User Authentication**: Register and login to access the library.
- **Book Search**: Search for books with various filters:
  - Search by title
  - Search by author
  - Search by genre
  - Search by uploader
- **Search Results**: Displayed as a table with:
  - Book cover pages
  - Title
  - Genres
  - Authors
  - Uploader's username
  - Options to download or read the book
  - Add/remove books to/from your shelf
- **Book Uploading**: Users can upload books by providing:
  - Title
  - Genre(s)
  - Author(s)
  - Cover page (image file)
  - Book (PDF file)
- **Shelf Management**: Easily add or remove books from your shelf.

## Technology Stack

- **Backend**: Flask
- **Database**: SQLite3
- **Requirements**: See [`requirements.txt`](/requirements.txt)

## Live Demo

You can check out the live version of the E-library [here](https://e-library-3jyx.onrender.com).

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request.

## Installation

To get started with the E-library project:

1. Clone the repository:
   ```bash
   git clone https://github.com/VijaySamant4368/E-library
   ```
2. Navigate to the project directory:
   ```bash
   cd E-library
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   flask run
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.

---

Feel free to reach out if you have any questions or suggestions!
