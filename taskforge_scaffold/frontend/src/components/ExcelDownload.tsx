import React from 'react';
export default function ExcelDownload({ url }) {
  return <a href={url} download>Download Spreadsheet</a>;
}
