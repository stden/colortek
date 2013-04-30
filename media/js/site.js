var Layout = {
	leftCol: undefined,
	rightCol: undefined,
	filterState: undefined // 0 - all closed, 1 - all opened, 2 - catalog selected
}, scrollBarWidth, initActionsHeight;

$(document).ready(function(){
	
	$('.main-page #main-filter .arr, .text-pages #main-filter .arr').css('cursor', 'pointer').click(function(){
		window.location.href = $('#main-filter ul.menu li.parent').eq(0).find('a').attr('href');
	});
	
	if ($('.action_list').length > 0){
		
		initActionsHeight = function(){
			
			$('.action_list .item .description').css('height', 'auto');
			
			var action_list_h = [],
				action_list_dh = [],
				action_list_th = [],
				aiH=0,
				ajH=0,
				amaxH = 0,
				aprevH = 0,
				aarH = [],
				asize = $('.action_list .item').length;
				
			$('.action_list .item').each(function(i){
				aiH++;
				ajH++;
				aarH[ajH-1] = $(this).find('.title');
				action_list_h[i] = $(this).find('.description').height();
				action_list_dh[i] = action_list_h[i] - 60;
				action_list_th[i] = $(this).find('.title').height();
				
				if (action_list_th[i] > aprevH) amaxH = action_list_th[i]
				aprevH = action_list_th[i]
				
				if(aiH%3==0 || asize == aiH){
					$.each(aarH, function(i, val){ val.height(amaxH); })
					aarH = null;
					aarH = [];
					ajH=0;
					amaxH=0;
					aprevH=0;
				}
				
			});
			
			$('#load-block .item').each(function(){
				if(iH%3==0 || sizeH==iH){
					$.each(arH, function(i, val){
						val.height(maxH);
					})
					arH = []; jH=0; maxH=0; prevH=0;
				}
			})
			$('.action_list .item .description').css('height', '60px');
		
			$('.action_list .item').hover(function(){
				var i = $('.action_list .item').index(this);
					if (action_list_dh[i] > 0){
						$(this).css({'margin-bottom': -action_list_dh[i], 'z-index': 100});
						$(this).find('.description').height(action_list_h[i]);
					}
			}, function(){
				var i = $('.action_list .item').index(this);
					if (action_list_dh[i] > 0){
						$(this).css({'margin-bottom': 0, 'z-index': 10});
						$(this).find('.description').height(60);
					}
			});
		}
		initActionsHeight();
	}
	
    //ignore # popups
    $('a[href=#]').click(function(e){
        e.preventDefault();
    });
	if ($('#avarage_deliver_time_fk').length > 0){
		$('#avarage_deliver_time_fk').timepicker();
	}
	if ($('#id_deliver_time').length > 0){
		$('#id_deliver_time').timepicker();
	}
	if ($('#0-id_avarage_deliver_time').length > 0){
		$('#0-id_avarage_deliver_time').timepicker();
	}
	
	$('body.inner-pages #main-filter .wrap-content .content ul.menu li.parent span.arr-toggle').click(function(){
		//$(this).parent('li.parent').find('.options').toggle();
		$(this).parent('li.parent').toggleClass('active');
		return false;
	});
	
	if ($('#b-top .region select').length){
		var params = {
			changedEl: "#b-top .region select",
			visRows: 15,
			scrollArrows: true
		}
		cuSel(params);
	}
	if ($('.contentform select').length){
		var params = {
			changedEl: ".contentform select",
			visRows: 10,
			scrollArrows: true
		}
		cuSel(params);
	}
	
	$('#b-top .navigation .menu .show-steps .arr').bind('click', function(){
		$('#b-top .b-steps-info').slideToggle(150, function(){ });
		$(this).parent().toggleClass('active');
	});

	var flipTimer;
	/*$('#content-wrap .content .card').mouseenter(function(){
		var self = $(this);
			if (flipTimer) clearTimeout(flipTimer);
			flipTimer = setTimeout(function(){
				self.find('.front').animate({'height':0}, 300, function(){
					self.find('.back').fadeIn(150);
					self.addClass('flip');
				});
			}, 500);
	}).mouseleave(function(){
		var self = $(this);
			clearTimeout(flipTimer);
			$('#content-wrap .content .card').stop().removeClass('flip');
			$('#content-wrap .content .card').find('.back').stop().hide();
			$('#content-wrap .content .card').find('.front').stop().animate({'height':246}, 150);
	});*/
	
	$('.b-supplements .toggle-button a').click(function(){
		$(this).parents('.b-supplements').toggleClass('active');
		return false;
	})
	
	initLabels();
	initCatalog();
	//initLoadMoreItems();
	initPopup();
	initRegform();
	
	if ($('input.date').length > 0){
		$('input.date').datepicker({
			showOn: "both",
            buttonImage: "/media/img/icon/calendar.png",
            buttonImageOnly: true,
			dateFormat: "dd.mm.yy"
		});
		$.datepicker.regional['ru']
	}
	if ($('input#id_expires').length > 0){
		$('input#id_expires').datepicker({
			showOn: "both",
            buttonImage: "/media/img/icon/calendar.png",
            buttonImageOnly: true,
			dateFormat: "dd.mm.yy"
		});
		$.datepicker.regional['ru']
	}
	
	
	if ($('.user-bonus-info').length > 0){
		var number = $('.user-bonus-info span.count').text(),
			numberWrapped = '';
		
			for (var i = 0; i < number.length; i++){
				numberWrapped += '<span>' + number.substr(i, 1) + '</span>';
			}
			
			$('.user-bonus-info span.count').html(numberWrapped);
	}
    $('.supplements').bind('click', function(){
        return false;
    });
	
	
		
	if ($('body').hasClass('catalog-pages') || $('body').hasClass('inner-pages')){
		
	} else {
		($('.b-adv').length > 0) ? $('body').removeClass('text-pages') : $('body').addClass('text-pages')
	}
	
});

categoryListHeights = function(){
	var maxH = 0,
		prevH = 0,
		iH = 0,
		jH = 0,
		arH = [],
		item = $('.partners .category_list .item'),
		total = item.length;
		
		item.each(function(){
			iH++; jH++;
			arH[jH-1] = $(this);
			if ($(this).height() > prevH) maxH = $(this).height();
			prevH = $(this).height();
			if (iH%3 == 0 || total == iH){
				$.each(arH, function(i, val){
					val.height(maxH);
				})
				arH = [];
				jH = 0;
				maxH = 0;
				prevH = 0;
			}
		})
}

drawColumns = function(v){
	
	var flag = v || false,
		leftColHeight = $('#main-filter .wrap-content').height(),
		rightColHeight = $('#content-wrap .content').height() || $('#content-wrap .vis').height(),
		left, right;
		
		if (!flag){
			left = Layout.leftCol || leftColHeight;
			right = Layout.rightCol || rightColHeight;
			
		} else {
			left = leftColHeight;
			right = rightColHeight;
		}
		
		if ((right < left)){
			if ($('body.inner-pages').length > 0 || $('body.text-pages').length > 0){
				//$('#content-wrap .content').height(left)
				if ($('#content-wrap .content').parents('.registration').length > 0) return false;
				$('#content-wrap .content').css('min-height', left);
			} else {
				if ($('.col-3 .card').length > 0){
					$('#content-wrap .vis').height(left - 184);
				}
			}
		}
}

setLayout = function(){
	var filterMenuItem = $('#main-filter .wrap-content .content ul.menu li.parent.active');
	Layout.leftCol = $('#main-filter .wrap-content').height();
	Layout.rightCol = $('#content-wrap .content').height() || $('#content-wrap .vis').height();
	if (filterMenuItem.length > 0){
		Layout.filterState = 2;
		if (filterMenuItem.length > 1) Layout.filterState = 1;
	} else  {
		Layout.filterState = 0;
	}
}

window.onload = function(){
	
	setLayout();
	drawColumns();
	categoryListHeights();
	
	$('.b-dish-list .item .subhead a.supplements').click(function(){
		var self = $(this),
			top = $(this).parent().parent().parent().offset().top + $(this).parents('.col').height(),
			left = $('.b-dish-list').offset().left,
			link = $(this).attr('data-href');
			
			$('#supPop').remove();
			if (link){
				$.ajax({
					type: "GET",
					url: link,
					success: function(data){
						
						
						
						function cloneForm(){
							var form = $('#add-addons-form'),
								form_action = form.attr('action'),
								form_method = form.attr('method'),
								form_html = form.html(),
								f = "<form class='addon form' id='add-addons-form' method='"+form_method+"' action='"+form_action+"'>" + form_html + "</form>";
								
							return f;
						}
						
						$('#supPop').remove();
						$('<div id="supPop"><div class="b-supplements active"><div class="supplements-options"><div class="col-2"><div class="col">'+ cloneForm() +'</div></div></div></div><div class="close">&times;</div><div class="arr"></div></div>').appendTo('body');
						$('#supPop #addons').remove();
						$(data).insertBefore('#supPop #add-addons-form input[type="submit"]');
						initLabels();
						$('#supPop')
							.hide().css({
								'position': 'absolute',
								'width': $('.b-dish-list').innerWidth(),
								'left': left,
								'top': top
							}).fadeIn(150);
						$('#supPop .arr').css({
							'left': self.parents('.col').offset().left - left + (self.parents('.col').width() - 15)/2
						});
						if ($('#supPop').height() + top > $('.mainSF').height()){
							var paddingHeight = $('#supPop').height() + top - $('.mainSF').height() + $('#footer').height();
								$('.b-dish-list').css('padding-bottom', paddingHeight);
								$('#side-basket').css('padding-bottom', paddingHeight);
						}
						$('html,body').animate({scrollTop: top - self.parents('.col').height()}, 300);
					},
					error: function () {
						$('#supPop').remove();
					}
				});
			}
						
			//alert($('#supPop').innerHeight());
			initLabels();
		return false;
	});
	$('#supPop .close').live('click', function(){
		$('#supPop').remove();
		$('.b-dish-list').css('padding-bottom', 0);
		$('#side-basket').css('padding-bottom', 0);
	});
	
	if ($('#inform-messages').length > 0){
		var textInformMessages = $('#inform-messages').html();
		$('<div>' + textInformMessages + '</div>').fancybox({
			'padding': 40,
			opacity: 0.2,
			helpers : {
				overlay : {
					css : {
						'background' : 'rgba(0, 0, 0, 0.2)'
					}
				}
			}
		}).trigger('click');
		
	}
	
	$('#main-filter .btm .arr').click(function(){
		var filterMenuItemActive = $('#main-filter .wrap-content .content ul.menu li.parent.active'),
			filterMenuItem = $('#main-filter .wrap-content .content ul.menu li.parent');
		if (filterMenuItemActive.length > 0){
			filterMenuItem.addClass('active');
			if (filterMenuItemActive.length > 1){
				filterMenuItem.removeClass('active');
				drawColumns(true);
			}
		} else  {
			filterMenuItem.addClass('active');
			drawColumns(false);
		}
		$(this).toggleClass('active');
		($('#main-filter .wrap-content .content ul.menu li.parent.active').length > 1) ? drawColumns(true) : drawColumns(false)
		return false;
	});
	
	//if ($('#movingline').length) $('#movingline ul').liScroll({travelocity: 0.05});
	movingLineSlider();
	if ($('body').hasClass('basket-is-active')) $('#side-basket').height($('.main').height() - $('#b-top').height());

	
	initBasket();
	initBackToTop();
	
	//$('.b-dish-list .item .image').hover(function(){
	$('.b-dish-list .item .image').live('mouseenter', function(){
        $('#pop-supplements').remove();
        var link = $(this).attr('data-img');
        if (link){
            $.ajax({
                type: "GET",
                url: link,
                success: function(data){
					$('#pop-supplements').remove();
                    $('<div id="pop-supplements">'+data+'<span class="arr"></span></div>').appendTo('body');
                },
				error: function () {
					$('#pop-supplements').remove();
				}
            });
        }
	});
    //}, function(){
	$('.b-dish-list .item .image').live('mouseleave', function(){
        $('#pop-supplements').remove();
    });
	//$('.b-dish-list .item .image').mousemove(function(event){
	$('.b-dish-list .item .image').live('mousemove', function(event){
        if (defPosition(event).x + 377 > $('body').width()){
            $('#pop-supplements').addClass('left').css({
                'left':defPosition(event).x - 377,
                'top':defPosition(event).y
            });
        } else {
            $('#pop-supplements').removeClass('left').css({
                'left':defPosition(event).x + 35,
                'top':defPosition(event).y
            });
        }
    });
	
	$('.b-item-list .item .image').live('mouseenter', function(){
        $('#pop-supplements').remove();
        var link = $(this).attr('data-img');
        if (link){
            $.ajax({
                type: "GET",
                url: link,
                success: function(data){
					$('#pop-supplements').remove();
                    $('<div id="pop-supplements">'+data+'<span class="arr"></span></div>').appendTo('body');
                },
				error: function () {
					$('#pop-supplements').remove();
				}
            });
        }
    });
	$('.b-item-list .item .image').live('mouseleave', function(){
        $('#pop-supplements').remove();
    });
	$('.b-item-list .item .image').live('mousemove', function(event){
        if (defPosition(event).x + 377 > $('body').width()){
            $('#pop-supplements').addClass('left').css({
                'left':defPosition(event).x - 377,
                'top':defPosition(event).y
            });
        } else {
            $('#pop-supplements').removeClass('left').css({
                'left':defPosition(event).x + 35,
                'top':defPosition(event).y
            });
        }
    });
	
	if ($('.tool').length > 0){
		$('.tool').tipTip({edgeOffset: 15});
	}
		
}

$(window).scroll(function(){
	//
});

function defPosition(event) {
      return {
            x: event.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft || window.scrollX) || event.pageX,
            y: event.clientY + (document.documentElement.scrollTop || document.body.scrollTop || window.scrollY)
      };
}

initBackToTop = function(){
	var showBackToTopStart = $('#main-filter .wrap-content').height() - $(window).height() + 90,
		showBackToTopStop = 20,
		leftPos = $('#main-filter .wrap-content').offset().left;
	
		if ($("#back-top").length > 0) $("#back-top").remove();
		
		if ($('body.inner-pages').length > 0){
			$('<div id="back-top"><a href="#b-top">Наверх</a></div>').appendTo('body');
			if ($('.b-adv').length > 0){
				$("#back-top").hide().css({
					'left': leftPos,
					'bottom': showBackToTopStop
				});
			} else {
				$("#back-top").hide().css({
					'left': leftPos,
					'bottom': 60
				});
			}
		}
		
		$(function () {
			$(window).scroll(function () {			
				(getScrollTop() > showBackToTopStart) ? $('#back-top').fadeIn(150) : $('#back-top').fadeOut(150);
				if ($('.b-adv').length > 0){
					if (getScrollTop() >= $('.main').height() - $(window).height() - $('.b-adv').height() - 20)
						if (getScrollTop() - $('.main').height() + $(window).height() + $('.b-adv').height() + 20 < 20){
							$("#back-top").css('bottom', 20)
						} else {
							$("#back-top").css('bottom', getScrollTop() - $('.main').height() + $(window).height() + $('.b-adv').height() + 20)
						}
				}
			});
			$('#back-top a').click(function () {
				$('body,html').animate({ scrollTop: 0 }, 600);
				return false;
			});
		});
}

initBasketScroll = function(){

	if ($('body').hasClass('basket-is-active')){
		var basketButton = $('body.basket-is-active .navigation .basket'),
			basketLeft,
			basketTop;
			
			if (basketButton.length){
				basketLeft = basketButton.offset().left;
				basketTop = basketButton.offset().top;
			} else {
				return false;				
			}
			
		if ($('#side-basket').length > 0){
			var basketTopFix = $('#side-basket .i').eq(0).offset().top,
				basketContentHeight = $('#side-basket .i').eq(0).innerHeight();
		}
		
		$(window).scroll(function () {
		if ($('body').hasClass('basket-is-active')){
			if (basketContentHeight + 48 < $(window).height()){
			
				if (getScrollTop() == $('#b-top').offset().top){
					$('#side-basket .i').eq(0).css({
						'position': 'relative',
						'top': 0,
						'padding-top': 15
					});
					basketButton.css({
						'position': 'static',
						'left': 0,
						'top': 0,
						'margin-top': -15
					});
					$('.navigation .user').css({
						'margin-right': 0
					})
				}
				
				if (getScrollTop() > $('#b-top').offset().top){
					basketButton.css({
						'position': 'fixed',
						'left': basketLeft,
						'margin-top':0,
						'top': 0
					});
					$('#side-basket .i').eq(0).css({
						'position': 'fixed',
						'width': $('#side-basket').width() - 23,
						'top': 0,
						'padding-top': 63
					});
					$('.navigation .user').css({
						'margin-right': 168
					})
				}
				
			}
		} else {
			$('.navigation .basket').css({
				'position': 'static',
				'left': 0,
				'top': 0,
				'margin-top': -15
			});
			$('.navigation .user').css({
				'margin-right': 0
			});
		}
		});
		
	}
	
}

$(function () {
	var body = $("body");
	var previousWidth = null;
	
	/*if (body.hasClass('inner-pages') || $('.partners .menu').length){
		if (!body.hasClass('text-pages')) return false;
	}*/
	
	var currentWidth = body.width();
	// Function that applies padding to the body to adjust its position.
	var resizeBody = function () {
		var currentWidth = body.width();
		if (currentWidth != previousWidth) {
			previousWidth = currentWidth;
			// Measure the scrollbar size
			body.css("overflow", "hidden");
			scrollBarWidth = body.width() - currentWidth;
			body.css("overflow", "auto");
			$('.mainSF').css({"width": body.width() - scrollBarWidth + "px"});
			$('#main-filter').css({"width": body.width() - scrollBarWidth + "px"});
		}
	};
	
	if ( $('.mainSF').height() <= $('body').height() ){
		if((navigator.userAgent.match(/iPhone/i))) {
			
		} else {
			resizeBody();
		}
	}
});

$(window).resize(function(){
	$(function () {
		var body = $("body");
		var previousWidth = null;
		
		/*if (body.hasClass('inner-pages') || $('.partners .menu').length){
			if (!body.hasClass('text-pages')) return false;
		}*/
		
		var currentWidth = body.width();
		// Function that applies padding to the body to adjust its position.
		var resizeBody = function () {
			var currentWidth = body.width();
			if (currentWidth != previousWidth) {
				previousWidth = currentWidth;
				// Measure the scrollbar size
				body.css("overflow", "hidden");
				scrollBarWidth = body.width() - currentWidth;
				body.css("overflow", "auto");
				$('.mainSF').css({"width": body.width() - scrollBarWidth + "px"});
				$('#main-filter').css({"width": body.width() - scrollBarWidth + "px"});
			}
		};
		if ( $('.mainSF').height() <= $('body').height() ){
			if((navigator.userAgent.match(/iPhone/i))) {
				
			} else {
				resizeBody();
			}
		} else {
			$('.mainSF').css({"width": "100%"});
			$('#main-filter').css({"width": "100%"});
		}
	});
});

function getScrollTop(){
    if(typeof pageYOffset!= 'undefined'){ // Most browsers
        return pageYOffset;
    } else {
        var B = document.body; //IE 'quirks'
        var D = document.documentElement; //IE with doctype
        D = (D.clientHeight) ? D : B;
        return D.scrollTop;
    }
}

jQuery.fn.liScroll = function(settings) {
	settings = jQuery.extend({
		travelocity: 0.07
	}, settings);
	return this.each(function(){
		var $strip = jQuery(this);
			$strip.addClass("newsticker")
			
		var stripWidth = 0;
		var $mask = $strip.wrap("<div class='mask'></div>");
		var $tickercontainer = $strip.parent().wrap("<div class='tickercontainer'></div>");
		var containerWidth = $strip.parent().parent().width(); //a.k.a. 'mask' width
		
			$strip.find("li").each(function(i){
				stripWidth += jQuery(this, i).innerWidth();
			});
			$strip.width(stripWidth);
			
		var defTiming = stripWidth/settings.travelocity;
		var totalTravel = stripWidth + containerWidth - 200;
		
			function scrollnews(spazio, tempo){
				$strip.animate({left: '-='+ spazio}, tempo, "linear", function(){
					$strip.css("left", containerWidth);
					scrollnews(totalTravel, defTiming);
				});
			}
			
			scrollnews(totalTravel, defTiming);
			$strip.hover(function(){
				jQuery(this).stop();
			}, function(){
				var offset = jQuery(this).offset();
				var residualSpace = offset.left + stripWidth;
				var residualTime = residualSpace/settings.travelocity;
					scrollnews(residualSpace, residualTime);
			});
	});
};

initLabels = function(){
	
	//var checkbox = $('input[type="checkbox"]');
	//	checkbox.click(function(){return false;});

	var label = $('label');
		
		label.each(function(i){
			if (label.find('input[type="radio"]').length > 0 || label.find('input[type="checkbox"]').length > 0){
				$(this).addClass('lbl');
				if ( $(this).children('input').attr("checked") ) $(this).addClass('active');
			}
		});
		label.click('click', function(){
			
			if ($(this).hasClass('allday')){
				if (!$(this).parents('.item').find('.lbl').eq(0).hasClass('active')){
					$(this).parents('.item').find('.allday').removeClass('active');
					$(this).parents('.item').find('.allday').find('input').removeAttr("checked");
					return false;
				}
				
			}
			
			if (label.find('input[type="radio"]').length > 0 || label.find('input[type="checkbox"]').length > 0 || (label.attr("for") && $(this).prev('input#'+label.attr("for")).length > 0) ){
				if (label.attr("for") && $(this).prev('input#'+label.attr("for")).length > 0){
					// checkbox
					($(this).hasClass('active')) ?  $(this).prev('input#'+label.attr("for")).removeAttr("checked") : $(this).prev('input#'+label.attr("for")).attr("checked", "checked");
					$(this).toggleClass('active');	
				} else {
					
					if ($(this).parents('.radiogroup').length > 0){
						// radio
						var name = $(this).children('input').attr("name");
							label.children('input[name=' + name + ']').parent().removeClass('active');
							label.children('input[name=' + name + ']').removeAttr("checked");
							$(this).children('input[name=' + name + ']').attr("checked", "checked");
							$(this).addClass('active');
					} else {
						// checkbox
						($(this).hasClass('active')) ?  $(this).find('input').removeAttr("checked") : $(this).find('input').attr("checked", "checked");
						$(this).toggleClass('active');					
					}
				}
				return false;
			}
		});
		
	
}

initCatalog = function(){
	initCatalogCountInput();
	initCatalogFilter();
	initCatalogFilterReset();
	initSpanSelect();
}

initBasket = function(){
	var toggleButton = $('.navigation .basket a'),
		basketHeight = $('#content-wrap .b-inner').eq(0).height();
		
		toggleButton.click(function(){
			if ($('body').hasClass('catalog-pages')){
				//if ($(this).parent().hasClass('empty')) return false;
				$('body').toggleClass('basket-is-active');
				$('#side-basket').height(basketHeight);
				if (!$('body').hasClass('basket-is-active')){
					$('.navigation .basket').css({
						'position': 'static',
						'left': 0,
						'top': 0,
						'margin-top': -15
					});
					$('.navigation .user').css({
						'margin-right': 0
					});
				}
				initBasketScroll();
			} else {
				document.location.href = String('/catalog/cart/');
			}
			return false;
		});
	initBasketScroll();
}

initCatalogCountInput = function(){
	var plus = $('.b-item-list .item .order-action .count .plus'),
		minus = $('.b-item-list .item .order-action .count .minus'),
		
		plus1 = $('.b-dish-list .plus'),
		minus1 = $('.b-dish-list .minus');
		
		plus.live('click', function(){
			var input = $(this).prev('input[type="text"]'),
				v = parseInt(input.val());
				v++;
				input.val(v);
		});
		minus.live('click', function(){
			var input = $(this).next('input[type="text"]'),
				v = parseInt(input.val());
				if (v > 1) v--;
				input.val(v);
		});
		plus1.live('click', function(){
			var input = $(this).parents('.order-options').find('input[type="text"]'),
				dataThreshold = parseInt($(this).attr('data-threshold')),
				v = parseInt(input.val());
				input.val(v + dataThreshold);
		});
		minus1.live('click', function(){
			var input = $(this).next('input[type="text"]'),
				dataThreshold = parseInt($(this).attr('data-threshold')),
				v = parseInt(input.val());
				if (v > -1 * dataThreshold) v = v + dataThreshold;
				input.val(v);
		});
}

initCatalogFilterReset = function(){
	var resetButton = $('#main-filter .reset-form a');
		resetButton.on('click', function(){
			/*$('#main-filter').find('input[type="radio"]').removeAttr("checked");
			$('#main-filter').find('input[type="checkbox"]').removeAttr("checked");
			$('#main-filter').find('label').removeClass('active');
			$('#main-filter').find('.search input[type="text"]').val('');
			$('#main-filter').find('#price-slider-amount').val(0);
			$('#price-slider').slider( "value", 0);*/
			window.location.href = $(this).parents('li.parent').find('a.header').click().attr('href');
			return false;
		})
}

initCatalogFilter = function(){
	var optBlock = $('.menu li.parent.active .filter-options'),
		queryCheckboxAttr = [],
		queryStr = '',
		minPriceOpts = '',
		href = $('.menu li.parent.active a.header').attr('href'),
		getSearchOpts = window.location.search;
		
		if (getSearchOpts.indexOf('minimal_cost=') >= 0) minPriceOpts = $('#main-filter ul.menu li.parent.active .price-slider-amount').val();
		
		optBlock.find('label').click(function(){
			//checkboxes
			queryCheckboxAttr = [];
			queryStr = '';
			optBlock.find('input[type="checkbox"]').each(function(){
				if ( $(this).attr("checked") ){
					queryCheckboxAttr.push($(this).attr('name') + '=' + $(this).val());
				}
			})
			for (var i = 0; i < queryCheckboxAttr.length; i++){
				(i == 0) ? queryStr += queryCheckboxAttr[i] : queryStr += '&' + queryCheckboxAttr[i];
			}
			if (minPriceOpts != ''){
				window.location.search = '?' + queryStr + '&minimal_cost=' + minPriceOpts;
			} else {
				window.location.search = '?' + queryStr;
			}
		});
		
	
	
}

initSpanSelect = function(){
	var span = $('.size-sel');
		
		span.live('click', function(){
			var self = $(this),
				minus = $(this).find('.minus'),
				plus = $(this).find('.plus'),
				sel = $(this).find('.selected'),
				max = parseInt(sel.attr('max-count')),
				addition = parseInt(sel.attr('addition-count')),
				v = parseInt(sel.text());
				
				$(this).addClass('active');
				
				minus.live('click', function(){
					if (v >= addition) v = v - addition;
						sel.text(v);
						self.find('input[type="hidden"]').val(v)
				});
				
				plus.live('click', function(){
					if (v >= max){
						v = max;
						return false;
					}
						v = v + addition;
						sel.text(v);
						self.find('input[type="hidden"]').val(v)
				});
				
		});
}

/*
initLoadMoreItems = function(){
	$('.load-more-content').on('click', function(){
		var link = $(this).attr('href'),
			list = $(this).prev('.b-item-list'),
			loadBlock = list.find('.items-loaded');
			if (link){
				$.ajax({
					type: "POST",
					url: link,
					success: function(data){
						if (list.length > 0 && loadBlock.length > 0){
							$(data).appendTo(loadBlock);
						}
					}
				});
			}
		return false;
	});
}
*/

initPopup = function(){
	var orderButton = $('#side-basket a.order-button'),
		orderEditButton = $('table.orders a.edit, .b-order-notification a.edit'),
		passwordRestoreButton = $('.password-restore-popup');
	//Order popup
	if (orderButton.length > 0){
		orderButton.fancybox({
			type: 'ajax',
			padding: 40,
			opacity: 0.2,
			afterShow: function(){
				initLabels();
				var params = {
					changedEl: ".p-order-form select",
					visRows: 15,
					scrollArrows: true
				}
				cuSel(params);
				if ($('input.date').length > 0){
					$('input.date').datepicker({
						showOn: "both",
						buttonImage: "/media/img/icon/calendar.png",
						buttonImageOnly: true,
						dateFormat: "dd.mm.yy"
					});
					$.datepicker.regional['ru']
				}
				if ($('#id_deliver_time').length > 0){
					$('#id_deliver_time').timepicker();
				}
				$('.rules').bind('click', function(){
					if ($(this).hasClass('active')){
						$('.p-order-form .postAjax').removeClass('notActive');
					} else {
						$('.p-order-form .postAjax').addClass('notActive');
					}
				})
				$('#id_contractoffer').bind('click', function(){
					if ($(this).hasClass('active')){
						if ($('.rules').hasClass('active')){
							$('.p-order-form .postAjax').removeClass('notActive');
						} else {
							$('.p-order-form .postAjax').addClass('notActive');
						}
					} else {
						$('.p-order-form .postAjax').addClass('notActive');
					}
				})
			},
			helpers : {
				overlay : {
					css : {
						'background' : 'rgba(0, 0, 0, 0.2)'
					}
				}
			}
		});
	}
	//
	//Order edit
	if (orderEditButton.length > 0){
		orderEditButton.fancybox({
			type: 'ajax',
			padding: 40,
			opacity: 0.2,
			afterShow: function(){
				//initLabels();
				var params = {
					changedEl: ".order-status",
					visRows: 15,
					scrollArrows: true
				}
				cuSel(params);
				$('.add-items').on('click', function(){
					$('<tr><td><input type="text" value=""></td><td><input type="text" value="" class="count"></td><td><input type="text" value="" class="count"></td><td><input type="text" value="" class="count"></td></tr>').insertAfter($(this).prev('table.orders').find('tr:last'));
					return false;
				});
			},
			helpers : {
				overlay : {
					css : {
						'background' : 'rgba(0, 0, 0, 0.2)'
					}
				}
			}
		});
	}
	//
	//password restore
	if (passwordRestoreButton.length > 0){
		passwordRestoreButton.fancybox({
			type: 'ajax',
			padding: 40,
			opacity: 0.2,
			afterShow: function(){
				
			},
			helpers : {
				overlay : {
					css : {
						'background' : 'rgba(0, 0, 0, 0.2)'
					}
				}
			}
		});
	}
	//
}

initRegform = function(){
	$('.contentform .line .time-block .item label').each(function(i){
		if ($(this).hasClass('active')) $(this).parent('.item').find('.cusel').removeClass('classDisCusel');
	});
	$('.contentform .line .time-block .item label').on('click', function(){
		if (!$(this).hasClass('allday')){
			if ($(this).hasClass('active')){
				$(this).parent('.item').find('.cusel').removeClass('classDisCusel');
			} else {
				$(this).parent('.item').find('.cusel').addClass('classDisCusel');
				if ($(this).parent('.item').find('.allday').hasClass('active')){
					$(this).parent('.item').find('label.allday').click();
				}
			}
		}
	});
	
	var cuselTOFrom = [], cuselTOTo = [];
	$('.contentform .line .time-block .item label.allday').each(function(i){
		var inp = $(this).parent('.item').find('input[type="hidden"]');
		cuselTOFrom.push(inp.eq(0).val());
		cuselTOTo.push(inp.eq(1).val());
		
		if (inp.eq(0).val() == '00:00' && inp.eq(1).val() == '23:59'){
			if (!$(this).hasClass('active')){
				$(this).click();
				$(this).parent('.item').find('.cusel').addClass('classDisCusel');
			}
		}
		
	});
	
	$('.contentform .line .time-block .item label.allday').bind('click', function(){
		if (!$(this).parents('.item').find('.lbl').eq(0).hasClass('active')) return false;
		$(this).parent('.item').find('.cusel').toggleClass('classDisCusel');
		
		var i = $('.contentform .line .time-block .item label.allday').index(this),
			cuselFrom = $(this).parent('.item').find('.cusel').eq(0),
			cuselTo = $(this).parent('.item').find('.cusel').eq(1),
			cuselFromText = cuselFrom.find('.cuselText'),
			cuselToText = cuselTo.find('.cuselText');
			
			if (cuselFrom.hasClass('classDisCusel')){
				cuselFromText.text('00:00');
				cuselFrom.find('input').val('00:00');
			} else {
				cuselFromText.text(cuselTOFrom[i]);
				cuselFrom.find('input').val(cuselTOFrom[i]);
			}
			if (cuselTo.hasClass('classDisCusel')){
				cuselToText.text('23:59');
				cuselTo.find('input').val('23:59');
			} else {
				cuselToText.text(cuselTOTo[i]);
				cuselTo.find('input').val(cuselTOTo[i]);
			}
		
	});
	$('.contentform a.add').on('click', function(){
		var clonedEL = $(this).prev('.clone'),
			cloned = clonedEL.clone();
			
			$(cloned).insertBefore(clonedEL);
	});
}

movingLineSlider = function(){
	if ($('#scroller').length > 0){
		
		var list = $('#scroller'),
			current = 0,
			animateTime = 10000,
			changeTime = 5000,
			stop = false,
			timeMove,
			left = 0,
						
			last = list.find('li:last'),
			preLast = last.prev(),
			first = list.find('li:first'),
			preFirst = first.next(),
			
			dX = first.width();
			
			last.clone().insertBefore(first);
			//preLast.clone().insertBefore(list.find('li:first'));
			first.clone().insertAfter(last);
			//preFirst.clone().insertAfter(list.find('li:last'));

			function moveLeft(){
				//stop = true;
				left = left - dX;
				list.find('ul').stop().animate({'left': -dX}, animateTime, 'linear', function(){
					list.find('li:first').clone().insertAfter(list.find('li:last'));
					list.find('li:first').remove();
					left = 0;
					list.find('ul').css('left', 0);
					dX = list.find('li:first').innerWidth();
					//stop = false;
					moveLeft();
				});
			}
			moveLeft();
			/*
			function run(){
				if (!stop){
					moveLeft();
					timeMove = setTimeout(run, changeTime);
					
				}
			}
			timeMove = setTimeout(run, changeTime);*/
		
		
	}
}

/* Russian (UTF-8) initialisation for the jQuery UI date picker plugin. */
jQuery(function($){
	$.datepicker.regional['ru'] = {
		closeText: 'Закрыть',
		prevText: '&#x3c;Пред',
		nextText: 'След&#x3e;',
		currentText: 'Сегодня',
		monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь', 'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
		//monthNamesShort: ['Янв','Фев','Мар','Апр','Май','Июн', 'Июл','Авг','Сен','Окт','Ноя','Дек'],
		monthNamesShort: ['Январь','Февраль','Март','Апрель','Май','Июнь', 'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
		dayNames: ['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота'],
		dayNamesShort: ['вск','пнд','втр','срд','чтв','птн','сбт'],
		dayNamesMin: ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'],
		weekHeader: 'Нед',
		dateFormat: 'dd.mm.yy',
		firstDay: 1,
		isRTL: false,
		showMonthAfterYear: false,
		yearSuffix: ''};
	$.datepicker.setDefaults($.datepicker.regional['ru']);
});

var postAjax = function(params){
    url = params.url;
    data = params.data;

    $.ajax(url, {
        dataType: params.dataType || 'json',
        data: data,
        type: "POST",
        crossDomain: params.crossDomain || false,
        success: function(response, state, jqXHR){
            if (params.success) params.success(response, state);
        },
        error: function(response, state, jqXHR){
            if (params.failure) params.failure(response, state);
        },
        beforeSend: function(xhrResponse, settings){
            xhrResponse.setRequestHeader('X-Force-XHttpResponse', 'on');
        }
    });
}

var updateFormErrors = function(form, errors, prefix){
    $('ul.errors').detach().remove();
	$('.b-error-list-msg').remove();
	$('.is-error-field').removeClass('is-error-field');
    prefix = prefix || false;
    for (el in errors){
        if (prefix){            
			if ($(form).find('#'+prefix+'id_' + el).attr('type') == 'hidden'){
				blk = $(form).find('#cuselFrame-'+prefix+'id_' + el);
			} else {
				blk = $(form).find('#'+prefix+'id_' + el);
			}
            if (blk.parent().find('span.name'))
                blk = blk.parent().find('span.name');
        } else {
            blk = $(form).find("#id_" + el);
        }
		
        ul = $("<ul class='errors'></ul>");
        for (i=0; i < errors[el].length; i++){
            li = $("<li>" + errors[el][i] + "</li>");
            li.appendTo(ul);
        }
        ul.insertBefore(blk);
		blk.addClass('is-error-field');
		ul.parents('.line').find('.required').addClass('is-error-field');
    }
	if ($('.p-order-form').length > 0 && $('.is-error-field').length > 0){
		$('<div class="b-error-list-msg">Заполните обязательные поля</div>').insertBefore($('.p-order-form .form .box').eq(0));
		if ($('#phone_code').hasClass('is-error-field') || $('#phone_number').hasClass('is-error-field')){
			$('<div class="phone_number_error">Номер телефона может содержать только цифры</div>').appendTo($('.b-error-list-msg'));
		} else {
			$('.phone_number_error').remove();
		}
		if ($('#id_deliver_date').hasClass('is-error-field') || $('#deliver_time').hasClass('is-error-field')){
			$('<div class="deliver_date_time_error">Проверьте правильность заполнения даты поставки</div>').appendTo($('.b-error-list-msg'));
		} else {
			$('.deliver_date_time_error').remove();
		}
		
	}
}

var postFormAjax = function(p){
    form = p.form;
    data = p.data || form.serialize();

    postAjax({
        url: p.url || form.attr('action'),
        data: data,
        success: function(response, code){
            var _form = (typeof response.form == 'undefined') ? {} : response.form;
            if (_form.errors){
                updateFormErrors(form, _form.errors);
            }
            else {
                // do something
                var message = noty({
                    text: p.successMsg || "Сохранено ;)",
                    type: "success",
                    dismissQueue: true,
                    timeout: (typeof p.notyTimeout == 'undefined') ? 2000 : p.notyTimeout
                });
                if (p.reloadPage || false ){
                    setTimeout(function(){
                        document.location.reload();
                    }, p.reloadTimeout || 2500);
                }
            }
            if (p.success) p.success(response);
        },
        failure: function(response, code){
            noty({
                text: p.failreMsg || "Что-то пошло не так",
                type: "error",
                dismissQueue: true
            });
        }
    }); //endd postAjax
}

function in_array(needle, haystack, strict) {
	// Checks if a value exists in an array
	var found = false, key, strict = !!strict;
	for (key in haystack) {
		if ((strict && haystack[key] === needle) || (!strict && haystack[key] == needle)) {
			found = true;
			break;
		}
	}
	return found;
}
function remove_from_array(array, element) {
	var newarray = [];
	for (var i = 0; i < array.length; i++) {
		if (array[i] != element)
			newarray.push(array[i]);
	}
	return newarray;
}