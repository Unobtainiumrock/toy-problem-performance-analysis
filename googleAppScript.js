// This google app script will act as an event listener for changes in the primary problems spreadsheet.
// Whenever changes are detected (edit to an existing row or a new row added), an index reference to the edited row is
// appended to the change_tracker sheet.

// The purpose of the change tracker sheet is to perform batch updates to the database that's synchronized with
// the problems spreadsheet. Batch updates to the PostgreSQL db will be performed daily at midnight.
function onEdit(e) {
  const sheet1Name = "problems";
  const logSheetName = "change_tracker";
  if (e.range.getSheet().getName() !== sheet1Name) return;

  const editedRow = e.range.getRow();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let logSheet = ss.getSheetByName(logSheetName);

  // Create the log sheet if it doesn't exist
  if (!logSheet) {
    logSheet = ss.insertSheet(logSheetName);
    logSheet.appendRow(["EditedRow"]);
  }

  // Append the edited row index to the log sheet
  logSheet.appendRow([editedRow]);
}

// To reduce memory usage, this next script will clear out the change tracker sheet after sending the batch update to the database
function clearChangeTracker() {
  const trackerName = "change_tracker";
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tracker = ss.getSheetByName(trackerName);
  tracker.deleteRows(2, tracker.getLastRow() - 1); // Clear all rows except the header
}
