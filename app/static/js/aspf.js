
$(document).ready(function(){
				jQuery.noConflict();

	(function($){

	$("#mainContainer").addClass("Toolsimple");

	$('input#study_date').prop('type','date');

	$('div#s_explore, div#s_search').click(function(){
		$('div#s_explore').toggleClass("choice");
		$('div#s_search').toggleClass("choice");
		$('div#explore').toggleClass("not-shown");
		$('div#search').toggleClass("not-shown");
	});

	$('input#excel').change(function(){
		var file = $(this).prop('files')[0];

		var data = new FormData();
      	data.append('myExcel', file);
		$.ajax({
			type: "POST",
			url: "excel",
			data: data,
			contentType: false,
			processData: false
			}).done(function(data,testStatus,jqXHR){
				results = JSON.parse(jqXHR.responseText);
				if (results.success){
					AS_dialog('Is the study completed ?');
				}
				else {
					AS_alert(results.msg);
				}
			});

	});

	$('form#study').on('submit', function(e){
		e.preventDefault();
		$.ajax({
			type: $(this).prop('method'),
			url: $(this).prop('action'),
			data: $(this).serialize()
		}).done(function(data,textStatus,jqXHR) {
			results = JSON.parse(jqXHR.responseText);		
				AS_alert(results.msg);
		});
		
	});

	$('button#query').click(function(e){
		txt = $('textarea#query_string').val();
		$.ajax({
			type: "POST",
			url: "query",
			data: JSON.stringify(txt),
			contentType: "application/json; charset=utf-8",
			dataType: "json"
		}).done(function(data,textStatus,jqXHR){
			results = JSON.parse(jqXHR.responseText);
			if (results.success){
				$('div#query_results').html(results.html);
			}else{
				AS_alert(results.msg);
			}
		});

	});

	$('select#spf').change(function() {
		let val = $(this).val();
		if (val == "meanSPF"){
			$('div#meanSPF').removeClass('not-shown');
			$('div#labeledSPF').addClass('not-shown');
		} else {
			$('div#meanSPF').addClass('not-shown');
			$('div#labeledSPF').removeClass('not-shown');
		}
	});

	$('button#ingredient_search').click(function(){
		var num = $('div#ingredients li').length;
		check = $("a.removeField").length;
		if (check < 11){
			elm = $('div#ingredients li').last();
			elm1 = elm.clone(true);
			elm.after(elm1);
			elm1.find("input").val('');
			elm1.find("input").first().attr("list","ing_list"+num);
			elm1.find("datalist").attr("id","ing_list"+num);
		}
	});

	$("a.removeField").click(function(e){
		check = $("a.removeField").length
		if (check > 1){
			elm = $(this).closest("li")
			elm.remove();
		}
		else {$(this).closest("li").find("input").val('')}
	});


	let timeout = null;
	let q_value = '';
	var elm_input = null;

	$('input.ingredient').on('keyup', function (e) {
		e.preventDefault();
		elm_input = $(this);
		var val = elm_input.val();
		if (q_value == val){
			return false;
		}
		q_value = val;

	    clearTimeout(timeout);
	    timeout = setTimeout(function () {
	        if (q_value != ''){
	        	//$('datalist#ing_list').html('');
	        	elm_input.parents("li").find('datalist').html('');
	        	$.ajax({
				type: "POST",
				url: "search",
				data: JSON.stringify(q_value),
				contentType: "application/json; charset=utf-8",
				dataType: "json"
				}).done(function(data,testStatus,jqXHR){
					q_value = '';
					results = JSON.parse(jqXHR.responseText);
					if (results.success){
						for (r of results.tradenames){
							//$('datalist#ing_list').append("<option value='"+r+"'></option>");
							elm_input.parents('li').find('datalist').append("<option value='"+r+"'></option>");
						}
						elm_input.blur();
					}
					else {
						AS_alert(results.msg);
					}
				});
	        }
		   }, 1000);
		});

	$('button#search, button#excel_export').click(function(){
		var excel = ($(this).attr("id") == "excel_export") ? true : false;

		if (!excel){
			$('div#search_results').html('');
			$('div#filterResult').html('');
			$('button#excel_export').addClass("not-shown");
		}

		var ingredient_list = [];
		var performance = null;
		$('div#ingredients li').each(function(){
			let ingredient = $(this).find('input').first().val();
			let operator = $(this).find('select').val();
			let value = $(this).find('input').last().val();
			if (ingredient != ''){
				ingredient_list.push({'ingredient':ingredient,'operator':operator,'value':value});
			}
		});

		if ($('div#meanSPF').hasClass('not-shown')){
			performance = {'field':'spf_label','operator': 'eq', 'value': $('div#labeledSPF select').val()};
		} else {
			performance = {'field': 'spf_mean','value1':$('div#meanSPF input').first().val(), 'value2':$('div#meanSPF input').last().val()}
		}

		query = {'performance':performance,'ingredients':ingredient_list, 'action':excel};

		$.ajax({
			type: "POST",
			url: "searchSPF",
			data: JSON.stringify(query),
			contentType: "application/json; charset=utf-8",
			dataType: "json"
		}).done(function(data,textStatus,jqXHR){
			results = JSON.parse(jqXHR.responseText);
			if (results.success){
				if (!excel){
					$('div#search_results').html(results.html);
					$('div#filterResult').html(results.html_filter);
					$('div#showSPFComposition').html('');
					$('button#excel_export').removeClass("not-shown");

					$('table#filter_result').find('td').each(function(){
							var html = $(this).html();
							$(this).html("<div class='filter_result'>"+html+"</div>");
					});

					let rows = $('table#filter_result tbody tr').length-2;
					$('table#filter_result tbody tr:eq('+rows+')').addClass("border-top");
					$('table#filter_result thead tr:eq(0)').addClass("border-bottom");

					$('table#search_result').find('td').each(function(){
						if ($(this).index() == 1 ){
							$(this).addClass('selectable_col');
						}
					});
				

				$('table#search_result td').click(function(){
					var col_index = $(this).index();
					var composition_id = $(this).html();
					if (col_index == 1) {
						$.ajax({
							type: "POST",
							url: "showComposition",
							data: JSON.stringify(composition_id),
							contentType: "application/json; charset=utf-8",
							dataType: "json"
							}).done(function(data,textStatus,jqXHR){
								results = JSON.parse(jqXHR.responseText);
								if (results.success){
									$('div#showSPFComposition').html(results.html);
								}else{
									AS_alert(results.msg);
								}
							})
					}
				});
				} // END of if excel
				else {
					var a = document.createElement("a");
					a.href = static+"xls/"+results.excel;
					a.click();
				}

			}else{
				AS_alert(results.msg);
			}
		});


	});

	
	$('button#queryMABS').click(function(e){
		txt = $('textarea#query_stringMABS').val();
		$.ajax({
			type: "POST",
			url: "queryMABS",
			data: JSON.stringify(txt),
			contentType: "application/json; charset=utf-8",
			dataType: "json"
		}).done(function(data,textStatus,jqXHR){
			results = JSON.parse(jqXHR.responseText);
			if (results.success){
				$('div#query_resultsMABS').html(results.html);
			}else{
				AS_alert(results.msg);
			}
		});

	});

	$('select#study_year').on("change",function(){
		var value = $(this).val();
		if (value != '') {
			$.ajax({
			type: "POST",
			url: "showStudies",
			data: JSON.stringify(value),
			contentType: "application/json; charset=utf-8",
			dataType: "json"
		}).done(function(data,textStatus,jqXHR){
			results = JSON.parse(jqXHR.responseText);
			if (results.success){
				$('div#showSPF').html('');
				$('div#showComposition').html('');
				$('div#showStudies').html(results.html);
				
				$('table#studies').find('td').each(function(){
					var html = $(this).html();
					$(this).html("<div class='limited_cell'>"+html+"</div>");
					if ($(this).index() == 0 ){
						$(this).addClass('selectable_col');
					}
				});

				$('table#studies td div').click(function(){
					var col_index = $(this).index();
					var study_id = $(this).html();
					if (col_index == 0) {
						$.ajax({
						type: "POST",
						url: "showSPF",
						data: JSON.stringify(study_id),
						contentType: "application/json; charset=utf-8",
						dataType: "json"
						}).done(function(data,textStatus,jqXHR){
							results = JSON.parse(jqXHR.responseText);
							if (results.success){
								$('div#showComposition').html('');
								$('div#showSPF').html(results.html);

								$('table#spf').find('td').each(function(){
								if ($(this).index() == 2 ){
									$(this).addClass('selectable_col');
									}
								});

								$('table#spf td').click(function(){
									var col_index = $(this).index();
									var composition_id = $(this).html();
									if (col_index == 2) {
										$.ajax({
											type: "POST",
											url: "showComposition",
											data: JSON.stringify(composition_id),
											contentType: "application/json; charset=utf-8",
											dataType: "json"
											}).done(function(data,textStatus,jqXHR){
												results = JSON.parse(jqXHR.responseText);
												if (results.success){
													$('div#showComposition').html(results.html);
												}else{
													AS_alert(results.msg);
												}
											})
									}
								});

							}else{
								AS_alert(results.msg);
							}

						});
					}
				});

			}else{
				AS_alert(results.msg);
			}
		});
		} else {
			$('div#showSPF').html('');
			$('div#showComposition').html('');
			$('div#showStudies').html('');
		}
	});



	function AS_alert(text){
		elm = $(".pop-up-alert")
		elm.find("span").html(text);
		elm.css("display", "block");
	}

	function AS_dialog(text){
		elm = $(".pop-up-dialog")
		elm.find("span").html(text);
		elm.css("display", "block");
	}

	$("button.cancel").click(function(){
		$("div.pop-up-alert").css("display","none");
		$("div.pop-up-dialog").css("display","none");
	});

	


})(jQuery); // end of self activating function to release $ for outher plugins
});	//END of document ready