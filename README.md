# WebAppSunScene

## Installation

See `install.txt` or `install_local.txt`

## Adding new features (Architecture)

### Web routes

The WebApp uses the python library flask for its backend.

The registered routes are:

- `/` : This route simply redirects to `/node/start`
- `/node/<name>/<identifier>` : 
  If `<identifier>` is not given, then a random unique 
  identifier will be computed. All subsequent calls 
  (in the session) will share this identifier.
  - GET: 
  The page serves the template `<name>.html`
  - POST: 
    The data posted by the user is recovered 
    in a dictionary by `request.form.to_dict()`. 
    The uploaded
    files are obtained by `request.files`.
  
    If the data contains the keyword `next_step`, 
    then the user will be redirected to this step.
    Otherwise, it will be redirected to `/end/\<identifier\>`.
    
  Special cases:
  
  - `/node/start/` : Is the first page called. 
  The first step in the decision tree must be hardcoded 
  in the template `start.html` 
  - `/node/confirm/\<identifier\>` : The last page in the 
  decision tree 
  must redirect to this page. After asking for 
  confirmation, it
  will redirect to `/end/<identifier>`.
  
- `/end/<identifier>` : 
When this route is called the processing starts (see below).
- `/status/<identifier>` : The `status.html` template
gives the current status of the computation.

- `/results/<identifier>` : The user gets the results 
in a zip file `output.zip`.

### Processing unit

The computation process is initiated when the user 
confirms the data in the `/node/confirm/<identifier>`
page and the function `process_request` is called with parameter 
`identifier` in a separate thread.

The function `process_request` processes the input using the 
imported function `processing_unit.process_input` 
and sends a mail with a 
link to the results page.

The module `processing_unit` imports all experiments found in 
the `experiments` package.

The guidelines for implementing such a module are:

* The name of the file must be the identifier given in the companion template
* It must implement a method `experiment(data, rootfolder).
  * `data` is a dictionary with the data given by the user
  * `rootfolder` is the name of the root folder of the experiment
* The files uploaded by the user are in `rootfolder/files`
* The output files must be put in `rootfolder/output`
* The file `rootfolder/status.json` must contain a json object with
structure:
    * key: `status`; 
    value: `started`, `running`, `finished` or `error`
    * key: `percentage`; value: number in the range 0..100 giving
the percentage of computation that is currently completed.
* A helper module ``webappsunscene.utils.statuslogger`` 
creates the ``status.json`` file and handle its updates.

