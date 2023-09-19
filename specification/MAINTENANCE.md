Maintenance of Video Metadata Hub specification files
-----------------------------------------------------

Setup:
- If you don't have the client_secret.json file locally, download it in JSON form
  from the Google Cloud API project page:
    https://console.cloud.google.com/apis/credentials?project=green-bedrock-150715
  Move this file to tools/client_secret.json.


1. To generate the VMHub HTML properties page:
   Edit the file `tools/constants.py` and ensure the values are correct:
    ```
    # Constant values
    StdVersion = "1.4"
    HeaderAppendix = "- DRAFT -"   # could be " - D-R-A-F-T - "
    IPTCApprovalDate = "19 Oct 2022"
    IPTCRevisionDate = "19 Oct 2022"
    CopyrightYear = "2022"
    SpreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
    RangeName = 'Properties 1.4 DRAFT!A3:W'
    ErrataRangeName = 'PropErrata!A3:E'
    ```    
    
   Run `tools/VMHprocessProps1.py`. This will create the file `IPTC-VideoMetadataHub-props-Rec_#.#.html`.

   Check the output locally in a browser. Ensure that the columns are all filled in, the version
   used is correct, and that the new and modified cells are correct (use 'n' and 'm' in the google
   sheet to mark new properties and modified cells).

2. To generate the VMHub HTML mappings page:
   Edit the file `tools/constants.py` is up to date, as per the above.

   Run `tools/VMHprocessMappings1.py`. This will create the file `IPTC-VideoMetadataHub-props-Rec_#.#.html`
   plus a mapping file for each mapped standard, eg `IPTC-VideoMetadataHub-mapping-SonyXDCAM-Rec_#.#.html` .

   Check the output locally in a browser. Ensure that the columns are all filled in, the version
   used is correct, and that the new and modified cells are correct (use 'n' and 'm' in the google
   sheet to mark new properties and modified cells).

3. Update the JSON Schema:
   Run `tools/VMHprocessJSONschema1.py`. This generates the snippet files `VMH-JSON-Schema-snip-refObjectproperties.json`
   and `VMH-JSON-Schema-snip-properties.json`.
   Check that the snippet file looks correct.
   Copy the schema skeleton to a skeleton for the new schema version:
   `cp iptc-vmhub-schema-skeleton.json /iptc-vmhub-1.5-schema.json`
   Open up the new file, go to the properties section and insert the *properties* snippet (on vim this is done using
    `:r VMH-JSON-Schema-snip-properties.json`).
   Use `check-jsonschema` to validate the example files:
    `check-jsonschema --schemafile iptc-vmhub-1.4-schema.json ../examples/json/VMH-JSON-Examples-*`
   You might have to remove the `dummy1` enums from the schema file, you can do that manually.

4. If everything looks good, copy it to https://www.iptc.org/std/videometadatahub/recommendation/.
   Put the previous version files in
   https://www.iptc.org/std/videometadatahub/recommendation/previous-versions/
