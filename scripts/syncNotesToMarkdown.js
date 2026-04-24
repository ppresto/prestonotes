/**
 * Google Apps Script — GDoc / PDF → Markdown under MyNotes on Drive (TASK-006).
 *
 * Deploy: Extensions → Apps Script, paste this file (or merge), then:
 *   1. Project Settings → Script properties → add MYNOTES_ROOT_FOLDER_ID (same value as .cursor/mcp.env).
 *   2. Optional time-based trigger → syncNotesToMarkdown().
 *
 * This does not run under Node; it uses DriveApp / UrlFetchApp / Advanced Drive service.
 * For Advanced Drive (Drive.Files.create with OCR), enable "Drive API" in Services (+).
 */

function syncNotesToMarkdown() {
  const rootId =
    PropertiesService.getScriptProperties().getProperty("MYNOTES_ROOT_FOLDER_ID") || "";
  if (!rootId) {
    Logger.log(
      "Set Script property MYNOTES_ROOT_FOLDER_ID (Drive folder ID for MyNotes root).",
    );
    return;
  }
  const rootFolder = DriveApp.getFolderById(rootId);

  Logger.log("Starting targeted GDoc sync inside: " + rootFolder.getName());
  syncGDocsInFolder(rootFolder, rootId);

  Logger.log("Starting targeted PDF OCR sync inside: " + rootFolder.getName());
  syncPdfsInFolder(rootFolder, rootId);

  Logger.log("All syncs complete.");
}

function syncGDocsInFolder(folder, rootFolderId) {
  const folderPath = getFolderPath(folder, rootFolderId);
  const docs = folder.getFilesByType(MimeType.GOOGLE_DOCS);
  const nameRegex = /.*Notes$/i;

  while (docs.hasNext()) {
    const doc = docs.next();
    const docName = doc.getName();

    if (!nameRegex.test(docName)) continue;

    const docId = doc.getId();
    const docUpdated = doc.getLastUpdated().getTime();
    const mdName = docName + ".md";

    const existingMdFiles = folder.getFilesByName(mdName);

    let mdFile = null;
    let mdUpdated = 0;

    if (existingMdFiles.hasNext()) {
      mdFile = existingMdFiles.next();
      mdUpdated = mdFile.getLastUpdated().getTime();
    }

    if (!mdFile || docUpdated > mdUpdated) {
      Logger.log(`[${folderPath}] -> Converting GDoc: ${docName}...`);
      convertToMd(docId, mdName, folder, mdFile);
    }
  }

  const subfolders = folder.getFolders();
  while (subfolders.hasNext()) {
    syncGDocsInFolder(subfolders.next(), rootFolderId);
  }
}

function convertToMd(docId, mdName, folder, existingMdFile) {
  const url = `https://docs.google.com/feeds/download/documents/export/Export?exportFormat=markdown&id=${docId}`;
  const options = {
    headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
    muteHttpExceptions: true,
  };

  const response = UrlFetchApp.fetch(url, options);

  if (response.getResponseCode() === 200) {
    const blob = response.getBlob().setName(mdName).setContentType("text/markdown");
    if (existingMdFile) {
      existingMdFile.setTrashed(true);
    }
    folder.createFile(blob);
    Logger.log(`Success: Created/Updated ${mdName}`);
  } else {
    Logger.log(`Error converting ${mdName}: ${response.getContentText()}`);
  }
}

function syncPdfsInFolder(folder, rootFolderId) {
  const folderPath = getFolderPath(folder, rootFolderId);
  const pdfs = folder.getFilesByType(MimeType.PDF);

  while (pdfs.hasNext()) {
    const pdf = pdfs.next();
    const pdfName = pdf.getName();
    const pdfUpdated = pdf.getLastUpdated().getTime();

    const mdName = pdfName.replace(/\.pdf$/i, ".md");
    const existingMdFiles = folder.getFilesByName(mdName);

    let mdFile = null;
    let mdUpdated = 0;

    if (existingMdFiles.hasNext()) {
      mdFile = existingMdFiles.next();
      mdUpdated = mdFile.getLastUpdated().getTime();
    }

    if (!mdFile || pdfUpdated > mdUpdated) {
      Logger.log(`[${folderPath}] -> Converting PDF (OCR): ${pdfName}...`);
      convertPdfToMd(pdf, mdName, folder, mdFile);
    }
  }

  const subfolders = folder.getFolders();
  while (subfolders.hasNext()) {
    syncPdfsInFolder(subfolders.next(), rootFolderId);
  }
}

function convertPdfToMd(pdfFile, mdName, folder, existingMdFile) {
  try {
    const blob = pdfFile.getBlob();

    const resource = {
      name: mdName + " (Temp OCR)",
      mimeType: MimeType.GOOGLE_DOCS,
    };

    const tempDocFile = Drive.Files.create(resource, blob, { ocr: true, ocrLanguage: "en" });

    const tempDoc = DocumentApp.openById(tempDocFile.id);
    const extractedText = tempDoc.getBody().getText();

    DriveApp.getFileById(tempDocFile.id).setTrashed(true);

    if (existingMdFile) {
      existingMdFile.setTrashed(true);
    }

    folder.createFile(mdName, extractedText, MimeType.PLAIN_TEXT);
    Logger.log(`Success: OCR Created/Updated ${mdName}`);
  } catch (e) {
    Logger.log(`Error OCR converting PDF ${pdfFile.getName()}: ${e.toString()}`);
  }
}

function getFolderPath(folder, rootFolderId) {
  let path = folder.getName();
  let parent = folder.getParents();
  while (parent.hasNext()) {
    const p = parent.next();
    if (p.getName() === "My Drive" || p.getId() === rootFolderId) break;
    path = p.getName() + "/" + path;
    parent = p.getParents();
  }
  return path;
}
