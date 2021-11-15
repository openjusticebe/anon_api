# PDF Document

- Tika Content type : application/pdf
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.pdf.PDFParser']

```
Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "access_permission:assemble_document",
  "access_permission:can_modify",
  "access_permission:can_print",
  "access_permission:can_print_degraded",
  "access_permission:extract_content",
  "access_permission:extract_for_accessibility",
  "access_permission:fill_in_form",
  "access_permission:modify_annotations",
  "dat_arr",
  "dc:format",
  "dcterms:created",
  "dcterms:modified",
  "dictum",
  "num_arr",
  "num_rol",
  "part",
  "pdf:PDFVersion",
  "pdf:charsPerPage",
  "pdf:docinfo:created",
  "pdf:docinfo:creator_tool",
  "pdf:docinfo:custom:dat_arr",
  "pdf:docinfo:custom:dictum",
  "pdf:docinfo:custom:num_arr",
  "pdf:docinfo:custom:num_rol",
  "pdf:docinfo:custom:part",
  "pdf:docinfo:modified",
  "pdf:docinfo:producer",
  "pdf:encrypted",
  "pdf:hasMarkedContent",
  "pdf:hasXFA",
  "pdf:hasXMP",
  "pdf:producer",
  "pdf:unmappedUnicodeCharsPerPage",
  "xmp:CreatorTool",
  "xmpTPg:NPages"
]
```


# DOCX Document

- Tika Content type : application/vnd.openxmlformats-officedocument.wordprocessingml.document
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.microsoft.ooxml.OOXMLParser']

```
Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "cp:revision",
  "dc:creator",
  "dc:publisher",
  "dcterms:created",
  "dcterms:modified",
  "extended-properties:AppVersion",
  "extended-properties:Application",
  "extended-properties:Company",
  "extended-properties:DocSecurity",
  "extended-properties:DocSecurityString",
  "extended-properties:Template",
  "meta:character-count",
  "meta:character-count-with-spaces",
  "meta:last-author",
  "meta:line-count",
  "meta:page-count",
  "meta:paragraph-count",
  "meta:print-date",
  "meta:word-count",
  "xmpTPg:NPages"
]
```

# DOC Document (MsWord pre 2003)

- Tika Content type : application/msword
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.microsoft.OfficeParser']

```
Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "cp:revision",
  "custom:AppVersion",
  "custom:Company",
  "custom:DocSecurity",
  "dc:creator",
  "dc:title",
  "dcterms:created",
  "dcterms:modified",
  "extended-properties:Template",
  "extended-properties:TotalTime",
  "meta:last-author",
  "meta:print-date"
]
```

# ODT Document

- Tika Content type : application/vnd.oasis.opendocument.text
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.odf.OpenDocumentParser']

Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "custom:AppVersion",
  "custom:Company",
  "custom:DocSecurity",
  "dc:creator",
  "dc:title",
  "dcterms:created",
  "dcterms:modified",
  "editing-cycles",
  "extended-properties:TotalTime",
  "generator",
  "meta:character-count",
  "meta:image-count",
  "meta:object-count",
  "meta:page-count",
  "meta:paragraph-count",
  "meta:table-count",
  "meta:word-count",
  "xmpTPg:NPages"
]

# RTF Document

- Tika Content type : application/rtf
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.microsoft.rtf.RTFParser']

```
Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "dc:creator",
  "dc:title",
  "dcterms:created",
  "extended-properties:Company"
]
```

# Plain text

- Tika Content type : text/plain; charset=UTF-8
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.csv.TextAndCSVParser']
```
Keys : [
  "Content-Encoding",
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis"
]
```

# EPUB Document

- Tika Content type : application/epub+zip
- Tika Content handler : ToTextContentHandler
- Tika Parser(s) : ['org.apache.tika.parser.DefaultParser', 'org.apache.tika.parser.epub.EpubParser']

```
Keys : [
  "Content-Type",
  "X-TIKA:Parsed-By",
  "X-TIKA:content",
  "X-TIKA:content_handler",
  "X-TIKA:embedded_depth",
  "X-TIKA:parse_time_millis",
  "dc:contributor",
  "dc:creator",
  "dc:identifier",
  "dc:language",
  "dc:publisher",
  "dc:title"
]
```
