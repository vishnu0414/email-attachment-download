# TODO: Add Preview Option for Attachments

## Tasks to Complete

### 1. Add preview route in app.py
- [x] Add `/preview/<int:attach_id>` route that serves attachment inline using `send_file` with `as_attachment=False`
- [x] Include user ownership check and file existence validation
- [x] Optionally add file type validation to restrict previews to safe types (images, PDFs, text files)

### 2. Update history.html template
- [x] Add preview button in the actions column of the attachments table
- [x] Link the button to the preview route with `target="_blank"` to open in new tab
- [x] Use appropriate icon and styling consistent with other buttons

### 3. Testing and Validation
- [ ] Test preview functionality to ensure it opens in new tab and displays attachments correctly
- [ ] Verify security checks (user ownership, file existence)
- [ ] Test with different file types to ensure proper inline display
