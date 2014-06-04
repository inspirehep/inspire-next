/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

$(document).ready( function() { 

	var article_related = $('*[class~="article-related"]');
	var thesis_related = $('*[class~="thesis-related"]');
	var chapter_related = $('*[class~="chapter-related"]');
	var book_related = $('*[class~="book-related"]');
	var proceedings_related = $('*[class~="proceedings-related"]');

	/**
	 * Hide form fields individually related to each document type
	 */
	function hideFields(){
		var field_list = [article_related,
						  thesis_related,
					   	  chapter_related,
					   	  book_related,
					   	  proceedings_related];
		$.map(field_list, function(field){
			field.parent().parent().slideUp();
		})
	}

	hideFields();

	var selected_type = $("#type_of_doc");
	selected_type.change(function(event) {
		hideFields();
		$('*[class~="'+selected_type.val()+'-related"]').parent().parent().slideDown();
			$('*[class~="'+selected_type.val()+'-related"]').parent().parent().parent().effect("highlight",
			{color: "#e1efbb"}, 2500);
		$("#collapse-2 .panel-body > .alert").remove('.alert');
		if(selected_type.val() == "proceedings"){
			var msg = "<strong>Proceedings:</strong> only for complete proceedings. \
					   For contributions use Article/Conference paper.";
			selected_type.parent().parent().parent().append(
				tpl_flash_message.render({state:'info',
										  message: msg}));
		}
	});

	/**
	 * Autofill form fields with given DOI, ArXiv id or ISBN data
	 *
	 * Uses REST API to query Crossref and the database to fetch data for
	 * the inputed ids.
	 */
	$("#importData").click(function() {
	//TODO: make function generic to fetch anything...add smaller functions for each source
		var btn = $(this);
		btn.button('loading');
		if($("#doi").val() != ''){
			// if DOI field is not empty
			var doi = $("#doi").val();
			var url = "/deposit/search_doi?doi=" + doi;
			var import_state, import_message;
			$.get(url, function( data ) {
				//thesis_types = ['book_series', 'book_title'];
				//var is_thesis = $.inArray(data.query.doi['type'], thesis_types) > -1;

				if(data.query.status == "success"){
					import_state = 'success';
					if(data.source == 'crossref'){
						import_message = 'The data was successfully imported from Crossref.';
						var title, authors, contributors;
						if(selected_type.val() == 'thesis'){
							title = data.query.volume_title;
						}
						else if(data.query.publication_type == 'full_text'){
							title = data.query.article_title;
							if(data.query.journal_title)
								$("#journal_title").val(data.query.journal_title);
							if(data.query.isbn)
								$("#isbn").val(data.query.isbn);
							if(data.query.first_page && data.query.last_page)
								$("#page_range").val(data.query.first_page + "-" + data.query.last_page);
							if(data.query.volume)
								$("#volume").val(data.query.volume);
							if(data.query.year)
								$("#year").val(data.query.year);
							if(data.query.issue)
								$("#issue").val(data.query.issue);
						}
						$("#title").val(title);
						authors = document.getElementById("field-authors");
						contributors = data.query.contributors;
							if(contributors && contributors.length>0 &&
							   contributors[0].contributor[0] &&
							   contributors[0].contributor[1].surname &&
							   contributors[0].contributor[0].given_name){
								authors.innerHTML = 
'<div class="authors dynamic-field-list ui-sortable" id="authors"> \
<input id="authors-__last_index__" name="authors-__last_index__" type="hidden" value="0">';
								for(i = 0; i<contributors.length; i++){
									var field = "#authors-" + i + "-name";
									authors.innerHTML +=
'<div class="field-list-element"> \
	<div class="row"> \
			<div id="authors-'+i+'"> \
					<div class="col-xs-6"> \
							<input class="form-control" id="authors-'+i+'-name" name="authors-'+i+'-name" type="text" value="'+contributors[i].contributor[1].surname +", "+contributors[i].contributor[0].given_name +'"> \
					</div> \
					<div class="col-xs-4 col-pad-0"> \
							<input class="form-control" id="authors-'+i+'-affiliation" name="authors-'+i+'-affiliation" placeholder="Affiliation" type="text" value=""> \
					</div> \
			</div> \
			<div class="col-xs-2"> \
					<a class="sort-element text-muted sortlink iconlink" rel="tooltip" title="Drag to reorder"> \
							<i class="fa fa-sort fa-fw"></i> \
					</a> \
					<a class="remove-element text-muted iconlink" rel="tooltip" title="Click to remove"> \
							<i class="fa fa-times fa-fw"></i> \
					</a> \
			</div> \
	</div> \
</div>';
								}
								authors.innerHTML +=
'<div class="empty-element"> \
<div class="row"> \
    <div id="authors-__index__"> \
        <div class="col-xs-6"> \
            <input class="form-control" id="authors-__index__-name" name="authors-__index__-name" placeholder="Family name, First name" type="text" value=""> \
        </div> \
        <div class="col-xs-4 col-pad-0"> \
            <input class="form-control" id="authors-__index__-affiliation" name="authors-__index__-affiliation" placeholder="Affiliation" type="text" value=""> \
        </div> \
    </div> \
    <div class="col-xs-2"> \
        <a class="sort-element text-muted sortlink iconlink" rel="tooltip" title="Drag to reorder"></a><a class="remove-element text-muted iconlink" rel="tooltip" title="Click to remove"></a> \
    </div> \
</div> \
</div> \
<div class="row"><div class="col-xs-12"> \
<span class="pull-right"> \
    <a class="add-element"> \
        <i class="fa fa-plus"></i> Add another author \
    </a> \
</span> \
</div> \
<p class="text-muted field-desc"><small>Required.</small></p> \
\
<div class="alert help-block" id="state-authors" style="margin-top: 5px; display: none;"></div>';
							}
					} else if(data.source == 'database'){
						// if DOI and the source is the database
						import_state = 'info';
						import_message = 'This DOI already exists in Inspire database.';
					}
				} else {
					// if DOI not found or malformed
					import_state = 'warning';
					if(data.query.status == 'notfound')
						import_message = 'The DOI ' + $("#doi").val() + ' was not found.';
					else if(data.query.status == 'malformed')
						import_message = 'The DOI ' + $("#doi").val() + ' is malformed.';
				}
				flash_import({state:import_state, message: import_message});
			});
		}
		else if($("#arxiv_id").val() != ''){
		   // if DOI field is empty and ArXiv has something
              var arxiv = $("#arxiv_id").val();
              var url = "/arxiv/search?arxiv=" + arxiv;
              var import_state, import_message;
              $.get(url, function( data ) {
                if(data.query.status == "success"){
                  import_state = 'success';
                  if(data.source == 'arxiv'){
                    import_message = 'The data was successfully imported from ArXiv.';
                    var title, authors, contributors;

                    if (selected_type.val() == 'article') {
                      title = data.query.title;
                      if(data.query.published)
                        $("#year").val(data.query.published);
                      if(data.query.summary)
                        $("#abstract").val(data.query.summary);
                      if(data.query.id)
                        $("#article_id").val(data.query.id);
                    }
                    $("#title").val(title);
                    authors = document.getElementById("field-authors");
                    contributors = data.query.author;
                      if(contributors && contributors.length>0){
                        authors.innerHTML =
        '<div class="authors dynamic-field-list ui-sortable" id="authors"> \
        <input id="authors-__last_index__" name="authors-__last_index__" type="hidden" value="0">';
                        for(i = 0; i<contributors.length; i++){
                          var field = "#authors-" + i + "-name";
                          authors.innerHTML +=
        '<div class="field-list-element"> \
          <div class="row"> \
              <div id="authors-'+i+'"> \
                  <div class="col-xs-6"> \
                      <input class="form-control" id="authors-'+i+'-name" name="authors-'+i+'-name" type="text" value="'+ contributors[i].name +'"> \
                  </div> \
                  <div class="col-xs-4 col-pad-0"> \
                      <input class="form-control" id="authors-'+i+'-affiliation" name="authors-'+i+'-affiliation" placeholder="Affiliation" type="text" value=""> \
                  </div> \
              </div> \
              <div class="col-xs-2"> \
                  <a class="sort-element text-muted sortlink iconlink" rel="tooltip" title="Drag to reorder"> \
                      <i class="fa fa-sort fa-fw"></i> \
                  </a> \
                  <a class="remove-element text-muted iconlink" rel="tooltip" title="Click to remove"> \
                      <i class="fa fa-times fa-fw"></i> \
                  </a> \
              </div> \
          </div> \
        </div>';
                        }
                        authors.innerHTML +=
        '<div class="empty-element"> \
        <div class="row"> \
            <div id="authors-__index__"> \
                <div class="col-xs-6"> \
                    <input class="form-control" id="authors-__index__-name" name="authors-__index__-name" placeholder="Family name, First name" type="text" value=""> \
                </div> \
                <div class="col-xs-4 col-pad-0"> \
                    <input class="form-control" id="authors-__index__-affiliation" name="authors-__index__-affiliation" placeholder="Affiliation" type="text" value=""> \
                </div> \
            </div> \
            <div class="col-xs-2"> \
                <a class="sort-element text-muted sortlink iconlink" rel="tooltip" title="Drag to reorder"></a><a class="remove-element text-muted iconlink" rel="tooltip" title="Click to remove"></a> \
            </div> \
        </div> \
        </div> \
        <div class="row"><div class="col-xs-12"> \
        <span class="pull-right"> \
            <a class="add-element"> \
                <i class="fa fa-plus"></i> Add another author \
            </a> \
        </span> \
        </div> \
        <p class="text-muted field-desc"><small>Required.</small></p> \
        \
        <div class="alert help-block" id="state-authors" style="margin-top: 5px; display: none;"></div>';
                      }
                  } else if(data.source == 'database'){
                    // if ArXiv and the source is the database
                    import_state = 'info';
                    import_message = 'This ArXiv already exists in Inspire database.';
                  }
                } else {
                  // if ArXiv not found or malformed
                  import_state = 'warning';
                  if(data.query.status == 'notfound')
                    import_message = 'The ArXiv ' + $("#arxiv_id").val() + ' was not found.';
                  else if(data.query.status == 'malformed')
                    import_message = 'The ArXiv ' + $("#arxiv_id").val() + ' is malformed.';
                }
                flash_import({state:import_state, message: import_message});
              });

		}
		else if($("#isbn").val() != ''){
			// if DOI and ArXiv fields are empty and ISBN has something
			import_state = 'info';
			import_message = 'The ISBN importing is not available at the moment.';
		}
		flash_import({state:import_state, message: import_message});
		btn.button('reset');
	});

	/**
	* Flash a message in the top.
	*/
	function flash_import(ctx) {
	  $('#flash-import').html(tpl_flash_message.render(ctx));
	  $('#flash-import').show('fast');
	}
});
