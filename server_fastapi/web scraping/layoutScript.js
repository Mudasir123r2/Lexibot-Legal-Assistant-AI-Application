var books = [
           "PLD",
           "SCMR",
           "MLD",
           "PCrLJ",
           "PTD",
           "PLC-Service",
           "PLC-Labour",
           "YLR",
           "CLC",
           "CLD",
           "GBLR",
];
var courts = [
    'SUPREME-COURT',
    'LAND-COMMISSION-PUNJAB',
'Supreme Appellate Court Northern Areas',
'PATNA-HIGH-COURT-INDIA',
'ALLAHABAD-HIGH-COURT-INDIA',
'SERVICE TRIBUNAL FOR MEMBERS OF SUBORDINATE JUDICIARY',
'Customs, Central Excise and Sales Tax Appellate Tribunal',
'CUSTOMS APPELLATE TRIBUNAL BENCH-II KARACHI',
'SUPREME-COURT-AZAD-KASHMIR',
'PAKISTAN-BAR-COUNCIL',
'FEDERAL-LABOUR-COURT',
'KARNATAKA-HIGH-COURT-INDIA',
'LABOUR-COURT-NWFP',
'INCOME-TAX-SETTLEMENT-COMMISSION',
'SERVICE-TRIBUNAL-AZAD-KASHMIR',
'SUPREME-COURT-CYPRUS',
'SPECIAL-COURT-(OFFENCES IN BANKS)-LAHORE',
'APPELLATE TRIBUNAL INLAND REVENUE ISLAMABAD BENCH',
'LABOUR-APPELLANT-TRIBUNAL-BALOCHISTAN',
'ANDHRA-PRADESH-HIGH-COURT-INDIA',
'CUSTOM,EXCISE-AND-SALES-TAX-APPELLATE-TRIBUNAL',
'N.-W.F.P. Service Tribunal',
'SINDH-CHIEF-COURT',
'PUNJAB-SUBORDINATE-JUDICIAL-SERVICE-TRIBUNAL',
'LAHORE-HIGH-COURT-LAHORE',
'CENTERL-BOARD-OF-REVENUE',
'FEDERAL-SHARIAT-COURT',
'ARBITRATOR-AWARD-SINDH',
'PRIVY-COUNCIL',
'REVENUE-DECISION-PUNJAB',
'JUDICIAL-COMMISSIONERS-COURT-PESHAWAR',
'INCOME-TAX-APPELLATE-TRIBUNAL-DHAKA',
'Gilgit-Baltistan Chief Court',
'SPECIAL-COURT-(TERRORIST ACTIVITIES)-KARACHI',
'ADMINISTRATIVE-TRIBUNAL-PUNJAB',
'PUNJAB-BAR-COUNCIL',
'SPECIAL-COURT-(SPEEDY TRIALS)-MULTAN',
'SPECIAL-APPELLATE-COURT-SINDH',
'NATIONAL-INDUSTRIAL-RELATIONS-COMMISSION',
'LABOUR-COURT-BALOCHISTAN',
'LABOUR-APPELLATE-TRIBUNAL-PUNJAB',
'CUSTODIAN-OF-EVACUEE-PROPERTY-SINDH',
'LABOUR-APPELLANT-TRIBUNAL-SINDH',
'PUNJAB SERVICE TRIBUNAL',
'LABOUR-APPELLATE-TRIBUNAL-NWFP',
'APPELLATE TRIBUNAL INLAND REVENUE (PAKISTAN) KARACHI',
'FEDERAL-LAND-COMMISSION',
'SUPREME-COURT-OF-INDIA',
'EMPLOYEES-SOCIAL-SECURITY-INSTITUTIONS-PUNJAB',
'LABOUR-COURT-PESHAWAR',
'ORISSA-HIGH-COURT-INDIA',
'SINDH SUBORDINATE JUDICIARY SERVICE TRIBUNAL',
'INLAND REVENUE APPELLATE TRIBUNAL OF PAKISTAN',
'BOARD-OF-REVENUE-NWFP',
'Northern Areas Court of Appeals',
'KHYBER-PAKHTUNKHWA-SUBORDINATE-JUDICIARY-SERVICE-TRIBUNAL',
'SPECIAL-APPELLATE-COURT-CUSTOMS-PESHAWAR',
'MADRAS-HIGH-COURT-INDIA',
'CUSTOMS APPELLATE TRIBUNAL  BENCH-II LAHORE',
'SINDH-AND-BALOCHISTAN-HIGH-COURT',
'SUPREME-APPELLATE-COURT',
'INCOME-TAX-APPELLATE-TRIBUNAL-LAHORE',
'APPELLATE-TRIBANAL-SINDH',
'APPELLATE-TRIBUNAL-BALOCHISTAN',
'PUNJAB-AND-HARYANA-HIGH-COURT-INDIA',
'GAUHATI-HIGH-COURT-INDIA',
'CUSTOMS-APPELLATE-TRIBUNAL-BENCH-I',
'CUSTOMS APPELLATE TRIBUNAL  BENCH-III KARACHI',
'INCOME-TAX-APPELLATE-TRIBUNAL-BANGLADESH',
'COMMISSIONER-WORKMENS-COMPENSATION-AND-AUTHORITY',
'CALCUTTA-HIGH-COURT-INDIA',
'KERALA-HIGH-COURT-INDIA',
'CORPORATE-LAW-AUTHORITY',
'APPELLANT-BENCH-SECURITY-AND-EXCHANGE-COMMISSION',
'APPELLATE-TRIBUNAL-PUNJAB',
'FOREGIN-EXCHANGE-APPELLATE-BOARD-LAHORE',
'DRUG-COURT-KARACHI',
'AJ & K-PUNJAB-SUBORDINATE-JUDICIAL-SERVICE-TRIBUNAL',
'SUPREME-COURT-USA',
'CUSTOMS-APPELLATE-TRIBUNAL-KARACHI',
'SUPREME-APPELLATE-COURT-SINDH',
'WEST-PAKISTAN-INDUSTRIAL-COURT',
'BAR-COUNCIL-TRIBUNAL-NWFP',
'SPECIAL-COURT-(SPEEDY TRIALS)-LAHORE',
'LABOUR-COURT-SINDH',
'Northern Areas Chief Court',
'SUPREME-COURT-BANGLADESH',
'NORTHERN AREAS SUPREME APPELLATE COURT',
'MONOPLY-CONTROL-AUTHORITY',
'KHYBER PAKHTUNKHWA SUBORDINATE JUDICIARY SERVICE TRIBUNAL',
'PUNJAB ELECTION TRIBUNAL',
'SPECIAL-COURT-(SINDH)-KARACHI',
'MYSORE-HIGH-COURT-INDIA',
'Supreme Court (AJ&K) ',
'LABOUR-APPELLANT-TRIBUNAL-QUETTA',
'ELECTION-TRIBUNAL-OF-PESHAWAR',
'Shariat Appellate Bench',
'CUSTOMS-APPELLATE-TRIBUNAL-LAHORE',
'GUJARAT-HIGH-COURT-INDIA',
'FEDERAL-COURT-OF-PAKISTAN',
'DHAKA-HIGH-COURT',
'CHIEF-COURT-GILGIT',
'SUPREME-APPELLANT-COURT-GILGIT-BALTISTAN',
'ADDITIONAL-SECRETARY-GOVT-OF-PAKISTAN-MINISTRY-OF-FINANCE-SINDH',
'JAMMU-AND-KASHMIR-HIGH-COURT-INDIA',
'RAJASTHAN-HIGH-COURT-INDIA',
'Environmental Tribunal Punjab',
'SUPREME-COURT',
'National Industrial Relations Commission',
'MADHYA-PRADESH-HIGH-COURT-INDIA',
'LABOUR-COURT-PUNJAB',
'SERVICE-TRIBUNAL-BALOCHISTAN',
'SHARIAT APPELLATE JURISDICTION',
'SERVICE-TRIBUNAL-PUNJAB',
'CUSTOMS-APPELLATE-TRIBUNAL-ISLAMABAD',
'SUPREME-COURT-OF-UK',
'ANDHRA-PRADESH-HIGH-COURT-INDIAANDHRA-PRADESH-HIGH-COURT-INDIA',
'WEST-PAKISTAN-BOARD-OF-REVENUE',
'SPECIAL-COURT-(OFFENCES IN BANKS)-KARACHI',
'ELECTION-TRIBUNAL-SINDH',
'DELHI-INDUSTRAIL-COURT-INDIA',
'LABOUR-APPELLATE-TRIBUNAL-AZAD-KASHMIR',
'APPELLATE-TRIBUNAL-AZAD-KASHMIR',
'KARACHI-HIGH-COURT-SINDH',
'CONSTITUTIONAL-COURT-OF-SOUTH-AFRICA',
'COURT-OF-APPEAL',
'ASSAM-NAGALAND-HIGH-COURT-INDIA',
'HYDERABAD-HIGH-COURT-INDIA',
'SERVICE-TRIBUNAL-NWFP',
'INLAND REVENUE APPELLATE TRIBUNAL OF PAKISTAN KARACHI',
'Enrolment Committee Pakistan Bar Council',
'APPELLATE-TRIBUNAL-ANTI-TERRORISM-SINDH',
'CENTRAL-GOVERNMENT-INDUSTRIAL-TRIBUNAL-DHANBAD',
'PUNJAB LABOUR APPELLATE TRIBUNAL',
'SERVICE-TRIBUNAL-SINDH',
'ELECTION-TRIBUNAL-NWFP',
'ASSAM-HIGH-COURT-INDIA',
'CUSTOMS-APPELLATE-TRIBUNAL-PESHAWAR',
'BANGLADESH-HIGH-COURT',
'SUPREME-APPELATE-COURT-GILGIT',
'SUPREME-COURT-OF-CANADA',
'BAR-COUNCIL-ELECTION-TRIBUNAL-QUETTA',
'ELECTION-TRIBUNAL-PUNJAB',
'NATIONAL-INDUSTRIAL-TRIBUNAL-BOMBAY-INDIA',
'WEST-PAKISTAN-INDUSTRIAL-APPELLATE-TRIBUNAL',
'IMPLEMENTATION-TRIBUNAL-FOR-NEWSPAPER-EMPLOYEE',
'SUPREME-COURT-INDIA',
'SUPREME-COURT-OF-UNITED-STATES',
'AUTHORITY-UNDER-PAYMENT-OF-WAGES-ACT',
'DELHI-HIGH-COURT-INDIA',
'WEST-PAKISTAN-LABOUR-COURT',
'BOMBAY-HIGH-COURT-INDIA',
'CUSTOMS,CENTRAL-EXCISE-AND-SALES-TAX-APPELLATE-TRIBUNAL',
'FEDERAL-SERVICE-TRIBUNAL',
'EAST-PAKISTAN-LABOUR-COURT',
'INCOME-TAX-APPELLATE-TRIBUNAL-PAKISTAN',
'LABOUR-APPELLATE-TRIBUNAL-SINDH',
'Customs, Federal Excise and Sales Tax Appellate Tribunal',
'HOUSE-OF-LORDS',
'APPELLATE-TRIBUNAL-ANTI-TERRORISM-PUNJAB',
'CHANCERY-DIVISION',
'WEST-PAKISTAN-LABOUR-APPELLATE-TRIBUNAL',
'Environmental Protection Tribunal Karachi',
'FEDERAL-TAX-OMBUDSMAN-PAKISTAN',
'ELECTION-COMMISSION-OF-PAKISTAN',
'BAR-COUNCIL-NWFP',
'SECURITIES-AND-EXCHANGE-COMMISSION-OF-PAKISTAN',
'EMPLOYEES-OLD-AGE-BENEFITS-INSTITUTION',
'LABOUR-APPELLATE-TRIBUNAL-BALOCHISTAN',
'SPECIAL-COURT-(CUSTOM)-KARACHI',
'LABOUR-APPELLANT-TRIBUNAL-NWFP',
'CHANDIGARH-HIGH-COURT-INDIA',
'CUSTODIAN-LAHORE',
'AUTHORITY-FOR-ADVANCE-RULINGS',
'SPECIAL-COURT-ISLAMABAD',
'ENVIRONMENTAL-PROTECTION-TRIBUNAL-KARACHI',
'ISLAMABAD-HIGH-COURT',
'PESHAWAR-HIGH-COURT',
'COMPETITION COMMISSION OF PAKISTAN',
'ELECTION-TRIBUNAL-OF-PAKISTAN',
'JOURNAL',
'HARYANA-HIGH-COURT-INDIA',
'HIMACHAL-PRADESH-HIGH-COURT-INDIA',
'BAR-COUNCIL-SINDH',
'SOCIAL-SECURITY-COURT-SINDH',
'JUDICIAL-COMMISSIONER-COURT-BALOCHISTAN',
'ELECTION-TRIBUNAL-BALOCHISTAN',
'BANKING-TRIBUNAL-NWFP',
'BAGHDAD-UL-JADID',
'INCOME-TAX-APPELLATE-TRIBUNAL-KARACHI',
'ISLAMABAD',
'MAHARASHTRA-HIGH-COURT-INDIA',
'PUNJAB-ENVIRONMENTAL-TRIBUNAL-LAHORE',
'HIGH-COURT-AZAD-KASHMIR',
'KHYBER PAKHTUNKHAW SERVICE TRIBUNAL',
'LABOUR-APPELLANT-TRIBUNAL-PUNJAB',
'CUSTODIAN-OF-EVACUEE-PROPERTY-LAHORE',
'ELECTION-TRIBUNAL-(AJ& K)',
'BOARD-OF-REVENUE-PUNJAB',
'NORTHERN AREAS CHIEF COURT GILGIT',
'BOARD-OF-REVENUE-SINDH',
'SHARIAT-COURT-AZAD-KASHMIR',
'ENVIRONMENTAL-TRIBUNAL-LAHORE',
'QUETTA-HIGH-COURT-BALOCHISTAN',
'BEFORE ARBITRAL TRIBUNAL',

];

function checkForChanges() {
    try {
        if ($("body").hasClass("modal-open") === true) {
            $("#livesite_action_buttons").hide();
        }
        else if ($("body").hasClass("modal-open") === false) {
            $("#livesite_action_buttons").show();
        }

        setTimeout(checkForChanges, 100);
    } catch (ex) { }
}

function LoadMoreAdvanceSearch() {
    var court = $('#Advance_Court_Name_Search_input').val();
    var judge = $('#Advance_Judge_Search_input').val();
    var lawyer = $('#Advance_Lawyer_Search_input').val();
    var appelant = $('#Advance_Party_Search_input').val();
    var nd = $('#Advance_Keyword_Search_input').val();
    var rule = $('#Advance_Rule_Search_input').val();
    //var ruleSection = $('#Advance_Rule_Section_Search_input').val();
    var act = $('#Advance_Act_Search_input').val();
    var actSection = $('#Advance_Section_Name_Search_input').val();
    var act1 = $('#Advance_Act_Two_Search_input').val();
    var act1Section = $('#Advance_Section_Name_Two_Search_input').val();
    var rowNo = parseInt($('#advanceSearchRowNo').val());
    rowNo = rowNo + 50;
    $('#advanceSearchRowNo').val(rowNo);
    // if (searchType == "caselaw") {
    //debugger;
    var book = nd.trim();
    if (book.indexOf("[") >= 0 || book.indexOf("]") >= 0) {
        var countopeningbrackets = 0;
        var countclosingbrackets = 0;
        for (var i = 0; i < book.length; i++) {
            if (book[i] == '[') {
                countopeningbrackets++;

            }
            if (book[i] == ']') {
                if (countclosingbrackets + 1 != countopeningbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }
                countclosingbrackets++;
            }
        }
        if (countopeningbrackets != countclosingbrackets) {
            $('#advanceErrorNotifier').show();
            return false;
        }

    }
    if (book.indexOf('\"') >= 0) {
        var count = 0;
        for (var i = 0; i < book.length; i++) {
            if (book[i] == '\"') {
                count++;
                if (count % 2 == 0) {
                    // book[i] = ']';
                    book = setCharAt(book, i, ']');
                }
                if (count % 2 != 0) {
                    //book[i] = '[';
                    // book = book.replaceAt(i, "");
                    book = setCharAt(book, i, '[');
                }
            }
        }
        if (count % 2 != 0) {
            $('#advanceErrorNotifier').show();
            return false;
        }

    }

    if (book.indexOf("<") >= 0 || book.indexOf(">") >= 0) {
        var countopeningbrackets = 0;
        var countclosingbrackets = 0;
        for (var i = 0; i < book.length; i++) {
            if (book[i] == '<') {
                countopeningbrackets++;

            }
            if (book[i] == '>') {
                if (countclosingbrackets + 1 != countopeningbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }
                countclosingbrackets++;
            }
        }
        if (countopeningbrackets != countclosingbrackets) {
            $('#advanceErrorNotifier').show();
            return false;
        }
        else {
            book = book.replace(/</g, "[");
            book = book.replace(/>/g, "]");
        }
    }
    $('#advanceErrorNotifier').hide();

    //}
    $.ajax({
        type: 'POST',
        data: {
            "court": court, "judge": judge,
            "lawyer": lawyer, "appelant": appelant,
            "nd": book, "rule": rule,
            "act": act, "actSection": actSection,
            "act1": act1, "act1Section": act1Section, "rowNo": rowNo
        },

        url: "../Login/LoadMoreAdvanceSearch",
        success:
    function (result) {
        if (result != "-1") {

            $("#moreAdvanceSearchResult").append(result);
                           
        } else {

            $('#readMoreAdvanceSearch').hide();
        }
                       
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}
                
$(document).ready(function () {
    try {

        $('.Advance_Search_btn').click(function () {
            var court = $('#Advance_Court_Name_Search_input').val();
            var judge = $('#Advance_Judge_Search_input').val();
            var lawyer = $('#Advance_Lawyer_Search_input').val();
            var appelant = $('#Advance_Party_Search_input').val();
            var nd = $('#Advance_Keyword_Search_input').val();
            var rule = $('#Advance_Rule_Search_input').val();
            //var ruleSection = $('#Advance_Rule_Section_Search_input').val();
            var act = $('#Advance_Act_Search_input').val();
            var actSection = $('#Advance_Section_Name_Search_input').val();
            var act1 = $('#Advance_Act_Two_Search_input').val();
            var act1Section = $('#Advance_Section_Name_Two_Search_input').val();
            // if (searchType == "caselaw") {
            //debugger;
            var book = nd.trim();
            if (book.indexOf("[") >= 0 || book.indexOf("]") >= 0) {
                var countopeningbrackets = 0;
                var countclosingbrackets = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '[') {
                        countopeningbrackets++;

                    }
                    if (book[i] == ']') {
                        if (countclosingbrackets + 1 != countopeningbrackets) {
                            $('#advanceErrorNotifier').show();
                            return false;
                        }
                        countclosingbrackets++;
                    }
                }
                if (countopeningbrackets != countclosingbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }

            }
            if (book.indexOf('\"') >= 0) {
                var count = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '\"') {
                        count++;
                        if (count % 2 == 0) {
                            // book[i] = ']';
                            book = setCharAt(book, i, ']');
                        }
                        if (count % 2 != 0) {
                            //book[i] = '[';
                            // book = book.replaceAt(i, "");
                            book = setCharAt(book, i, '[');
                        }
                    }
                }
                if (count % 2 != 0) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }

            }

            if (book.indexOf("<") >= 0 || book.indexOf(">") >= 0) {
                var countopeningbrackets = 0;
                var countclosingbrackets = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '<') {
                        countopeningbrackets++;

                    }
                    if (book[i] == '>') {
                        if (countclosingbrackets + 1 != countopeningbrackets) {
                            $('#advanceErrorNotifier').show();
                            return false;
                        }
                        countclosingbrackets++;
                    }
                }
                if (countopeningbrackets != countclosingbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }
                else {
                    book = book.replace(/</g, "[");
                    book = book.replace(/>/g, "]");
                }
            }
            $('#advanceErrorNotifier').hide();

            //}
            $.ajax({
                type: 'POST',
                data: {
                    "court": court, "judge": judge,
                    "lawyer": lawyer, "appelant": appelant,
                    "nd": book, "rule": rule,
                    "act": act, "actSection": actSection,
                    "act1": act1, "act1Section": act1Section,"rowNo": 0
                },

                url: "../Login/AdvanceSearch",
                success:
            function (result) {
                $("#rightmenu").empty();
                $("#rightmenu").html(result);
            },
            error: function (res) {
                AjaxFailure(res);
            }
        });
    });
    $('.advance_search_main_content_div').keypress(function (e) {
        if (e.which == 13) {
            //debugger;
            var court = $('#Advance_Court_Name_Search_input').val();
            var judge = $('#Advance_Judge_Search_input').val();
            var lawyer = $('#Advance_Lawyer_Search_input').val();
            var appelant = $('#Advance_Party_Search_input').val();
            var nd = $('#Advance_Keyword_Search_input').val();
            var rule = $('#Advance_Rule_Search_input').val();
            // var ruleSection = $('#Advance_Rule_Section_Search_input').val();
            var act = $('#Advance_Act_Search_input').val();
            var actSection = $('#Advance_Section_Name_Search_input').val();
            var act1 = $('#Advance_Act_Two_Search_input').val();
            var act1Section = $('#Advance_Section_Name_Two_Search_input').val();
            var book = nd.trim();
            if (book.indexOf("[") >= 0 || book.indexOf("]") >= 0) {
                var countopeningbrackets = 0;
                var countclosingbrackets = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '[') {
                        countopeningbrackets++;

                    }
                    if (book[i] == ']') {
                        if (countclosingbrackets + 1 != countopeningbrackets) {
                            $('#advanceErrorNotifier').show();
                            return false;
                        }
                        countclosingbrackets++;
                    }
                }
                if (countopeningbrackets != countclosingbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }

            }
            if (book.indexOf('\"') >= 0) {
                var count = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '\"') {
                        count++;
                        if (count % 2 == 0) {
                            // book[i] = ']';
                            book = setCharAt(book, i, ']');
                        }
                        if (count % 2 != 0) {
                            //book[i] = '[';
                            // book = book.replaceAt(i, "");
                            book = setCharAt(book, i, '[');
                        }
                    }
                }
                if (count % 2 != 0) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }

            }

            if (book.indexOf("<") >= 0 || book.indexOf(">") >= 0) {
                var countopeningbrackets = 0;
                var countclosingbrackets = 0;
                for (var i = 0; i < book.length; i++) {
                    if (book[i] == '<') {
                        countopeningbrackets++;

                    }
                    if (book[i] == '>') {
                        if (countclosingbrackets + 1 != countopeningbrackets) {
                            $('#advanceErrorNotifier').show();
                            return false;
                        }
                        countclosingbrackets++;
                    }
                }
                if (countopeningbrackets != countclosingbrackets) {
                    $('#advanceErrorNotifier').show();
                    return false;
                }
                else {
                    book = book.replace(/</g, "[");
                    book = book.replace(/>/g, "]");
                }
            }
            $('#advanceErrorNotifier').hide();
            $.ajax({
                type: 'POST',
                data: {
                    "court": court, "judge": judge,
                    "lawyer": lawyer, "appelant": appelant,
                    "nd": book, "rule": rule,
                    "act": act, "actSection": actSection,
                    "act1": act1, "act1Section": act1Section, "rowNo": 0
                },

                url: "../Login/AdvanceSearch",
                success:
            function (result) {
                $("#rightmenu").empty();
                $("#rightmenu").html(result);
            },
            error: function (res) {
                AjaxFailure(res);
            }
        });

    }
    });
function advacneJudgeAjax(word) {
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetjudgeDropDown",
        success:
    function (result) {
        $("#Advance_Judge_Search_input").typeahead('destroy');
        $("#Advance_Judge_Search_input").typeahead({
            source: result
        }).on('keyup', this, function (event) {
            // debugger;
            var length = $('#Advance_Judge_Search_input').val().trim().length;
            if (length == 1) {
                var word = $('#Advance_Judge_Search_input').val();
                //alert(word);
                advacneJudgeAjax(word);
            }
                            
        });
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}
$('#Advance_Judge_Search_input').keyup(function () {
    var length = $('#Advance_Judge_Search_input').val().trim().length;
    if (length >= 3) {
        var word = $('#Advance_Judge_Search_input').val();
        //alert(word);
        advacneJudgeAjax(word);
    }

});
function advacneRuleAjax(word) {
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetRuleDropDown",
        success:
    function (result) {
        $("#Advance_Rule_Search_input").typeahead('destroy');
        $("#Advance_Rule_Search_input").typeahead({
            source: result
        }).on('keyup', this, function (event) {
            // debugger;
            var length = $('#Advance_Rule_Search_input').val().trim().length;
            if (length == 1) {
                var word = $('#Advance_Rule_Search_input').val();
                //alert(word);
                advacneRuleAjax(word);
            }
                            
        });
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}
               
//rule section
$('#Advance_Rule_Search_input').keyup(function () {
    var length = $('#Advance_Rule_Search_input').val().trim().length;
    if (length >= 3) {
        var word = $('#Advance_Rule_Search_input').val();
        //alert(word);
        advacneRuleAjax(word);
    }
});
function advanceActTwoSection(word) {
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetStatueSectionDropDown",
        success:
    function (result) {
        $("#Advance_Section_Name_Two_Search_input").typeahead('destroy');
        $("#Advance_Section_Name_Two_Search_input").typeahead({
            hint: true,
            highlight: true,
            minLength: 0,
            source: result
        });

        ev = $.Event("keydown")
        ev.keyCode = ev.which = 40
        $('#Advance_Section_Name_Two_Search_input').trigger(ev)

        //$("#Advance_Section_Name_Search_input").on('focus', $("#Advance_Section_Name_Search_input").typeahead.bind($("#Advance_Section_Name_Search_input"), 'lookup'));
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}
function advanceActTwoAjax(word){
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetStatueDropDown",
        success:
    function (result) {
        $("#Advance_Act_Two_Search_input").typeahead('destroy');
        $("#Advance_Act_Two_Search_input").typeahead({
            source: result
        }).on('keyup', this, function (event) {
            // debugger;
            var length = $('#Advance_Act_Two_Search_input').val().trim().length;
            if (length == 1) {
                var word = $('#Advance_Act_Two_Search_input').val();
                advanceActTwoAjax(word);

            }
        }).on('blur', this, function (event) {
            var length = $('#Advance_Act_Two_Search_input').val().trim().length;
            if (length >= 3) {
                var word = $('#Advance_Act_Two_Search_input').val();
                $("#Advance_Section_Name_Two_Search_input").val("");
                advanceActTwoSection(word)
            }
        });
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}
//act/ordinance1
$('#Advance_Act_Two_Search_input').keyup(function () {

    var length = $('#Advance_Act_Two_Search_input').val().trim().length;
    if (length >= 3) {
                        
        var word = $('#Advance_Act_Two_Search_input').val();
        advanceActTwoAjax(word);
                       
    }
});
$('#Advance_Section_Name_Two_Search_input').focus(function () {
    var length = $('#Advance_Act_Two_Search_input').val().trim().length;
    if (length >= 3) {
        var word = $('#Advance_Act_Two_Search_input').val();
        //alert(word);
        $.ajax({
            type: 'POST',
            data: {
                "word": word
            },
            global: false,
            url: "../Login/GetStatueSectionDropDown",
            success:
        function (result) {
            $("#Advance_Section_Name_Two_Search_input").typeahead('destroy');
            $("#Advance_Section_Name_Two_Search_input").typeahead({
                hint: true,
                highlight: true,
                minLength: 0,
                source: result
            });

            ev = $.Event("keydown")
            ev.keyCode = ev.which = 40
            $('#Advance_Section_Name_Two_Search_input').trigger(ev)

            //$("#Advance_Section_Name_Search_input").on('focus', $("#Advance_Section_Name_Search_input").typeahead.bind($("#Advance_Section_Name_Search_input"), 'lookup'));
        },
        error: function (res) {
            AjaxFailure(res);
        }
    });
}
});
function advanceActSearchResult(word) {
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetStatueDropDown",
        success:
    function (result) {
        $("#Advance_Section_Name_Search_input").typeahead('destroy');
        advanceActSuccessCallBack(result);
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
}

function advanceActSuccessCallBack(result) {

    $("#Advance_Act_Search_input").typeahead('destroy');
    $("#Advance_Act_Search_input").typeahead({
        source: result
    }).on('keyup', this, function (event) {
        // debugger;
        var length1 = $('#Advance_Act_Search_input').val().trim().length;
        if (length1 == 1) {
            $("#Advance_Section_Name_Search_input").typeahead('destroy');
            var word1 = $('#Advance_Act_Search_input').val();
            advanceActSearchResult(word1);
        }
    }).on('blur', this, function (event) {
        var word = $('#Advance_Act_Search_input').val();
        $("#Advance_Section_Name_Search_input").val("");
        advanceActSectionResult(word)
    });
}
//act/ordinance
$('#Advance_Act_Search_input').keypress(function () {
    //debugger;
    var length = $('#Advance_Act_Search_input').val().trim().length;
    if (length >= 3) {
        //debugger;
        var word = $('#Advance_Act_Search_input').val();
        //alert(word);
        advanceActSearchResult(word);
    }
});

function advanceActSectionResult(word) {
    // debugger;
                   
    $.ajax({
        type: 'POST',
        data: {
            "word": word
        },
        global: false,
        url: "../Login/GetStatueSectionDropDown",
        success:
    function (result) {
        $("#Advance_Section_Name_Search_input").typeahead('destroy');
        $("#Advance_Section_Name_Search_input").typeahead({
            hint: true,
            highlight: true,
            minLength: 0,
            source: result
        });

        ev = $.Event("keydown")
        ev.keyCode = ev.which = 40
        $('#Advance_Section_Name_Search_input').trigger(ev)

        //$("#Advance_Section_Name_Search_input").on('focus', $("#Advance_Section_Name_Search_input").typeahead.bind($("#Advance_Section_Name_Search_input"), 'lookup'));
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
                    
}
$('#Advance_Section_Name_Search_input').focus(function () {
    // debugger;
    var length = $('#Advance_Act_Search_input').val().trim().length;
    if (length >= 3) {
        var word = $('#Advance_Act_Search_input').val();
        //alert(word);
        $.ajax({
            type: 'POST',
            data: {
                "word": word
            },
            global: false,
            url: "../Login/GetStatueSectionDropDown",
            success:
        function (result) {
            $("#Advance_Section_Name_Search_input").typeahead('destroy');
            $("#Advance_Section_Name_Search_input").typeahead({
                hint: true,
                highlight: true,
                minLength: 0,
                source: result
            });

            ev = $.Event("keydown")
            ev.keyCode = ev.which = 40
            $('#Advance_Section_Name_Search_input').trigger(ev)

            //$("#Advance_Section_Name_Search_input").on('focus', $("#Advance_Section_Name_Search_input").typeahead.bind($("#Advance_Section_Name_Search_input"), 'lookup'));
        },
        error: function (res) {
            AjaxFailure(res);
        }
    });
}
});

$(checkForChanges);

$("#whatsNewTable td").click(function () {
    var category = $(this).text();
    //var month = $('#whatsNewTableMonth').text();
    if (jQuery.trim(category).length > 0) {
        $("#whatsNewTable td").removeClass("selectedDigestTD");
        $(this).addClass("selectedDigestTD");
    }
});

$('.miscellaneous').click(function () {
    //debugger;
    var type = $(this).attr('MiscellaneousType');
    var category = "";
    if (type == 1) {
        category = "circular";
    } else if (type == 2) {
        category = "general order";
    } else if (type == 3) {
        category = "notification";
    }
    $.ajax({
        type: 'POST',
        data: {
            "category": category, "desc": null, "year": null
        },
        url: "../Login/GetMiscellaneous",
        success:
    function (result) {
        $("#rightmenu").empty();
        $("#rightmenu").html(result);
        $('#miscellaneousHeading').html(category);
    },
    error: function (res) {
        AjaxFailure(res);
    }
});
});



} catch (ex) { }
});


        
function feedBackForm() {
    try{
        $.get("../Login/FeedBackForm", function (data) {
                    
            $('#feedBackFormBody').html(data);
                    
            $("#feedBackFormBody").removeData("validator");
            $("#feedBackFormBody").removeData("unobtrusiveValidation");
            $.validator.unobtrusive.parse("#feedBackFormBody");
            $('#FeedBackFormModal').modal('show');

        });
    } catch (ex) { }
}

function textField() {
    $('#searchLabel').text('Case Law Search');
    $('#yearSearch').hide();
    $('#courtSearch').show();
    $('#codeOrPageSearch').hide();
    $('#bookSearch').show();
    $('#caseLawYear').show();
    $('.quad-input').find('.form-control').css('width', '33%');
    $('#bookSearch').attr('placeholder', 'Enter Keyword');
    $('.searchButton ').removeClass('slectedButton');
    $('.searchButton').first().addClass('slectedButton');
    // $('.searchButton').first().css('background-color', '#366bff');
}

$(document).ready(function () {
    try{
        $(".case_description_modal_body").scrollbar();
                
        $('#searchbtn_hit').click(function () {

            $("#searchtext").removeHighlight();
            var text = $('#query').val();
            $("#searchtext").highlight(text);
            if ($('.highlight:first').length) {             //if match found, scroll to where the first one appears
                $('#ExceptionResponseScreen1').scrollTop($('.highlight:first').position().top);
            }
        });

        $('#query').keypress(function (e) {
            if (e.which == 13) {

                $("#searchtext").removeHighlight();
                var text = $('#query').val();
                $("#searchtext").highlight(text);
                if ($('.highlight:first').length) {             //if match found, scroll to where the first one appears
                    $('#ExceptionResponseScreen1').scrollTop($('.highlight:first').position().top);
                }
            }
        });
        $('#searchLabel').text('Case Law Search');
        $('#yearSearch').hide();
        $('#courtSearch').show();
        $('#codeOrPageSearch').hide();
        $('#bookSearch').show();
        $('#caseLawYear').show();
        $('.quad-input').find('.form-control').css('width', '33%');
        $('#bookSearch').css('width', '47%');
        $('#caseLawYear').css('width', '20%');
        $('#bookSearch').attr('placeholder', 'Enter Keyword');

        var currentTime = new Date();
        var year = currentTime.getFullYear() - 5;
        $('#yearSearch').val(year);
        $('#caseLawYear').change(function () {
            var rec = $(this).val();

            var currentTime = new Date();
            var year = currentTime.getFullYear() - rec;

            $('#yearSearch').val(year);
        });
        $('#citationCategory').change(function () {
            var rec = $(this).val();
            $('#bookSearch').val(rec);
        });

        $('#whatsNewTable td').click(function () {
            // debugger;
            var category = $(this).text();
            var month = $('#whatsNewTableMonth').text();
            if (jQuery.trim(category).length > 0) {

                $.ajax({
                    type: 'POST',
                    data: {
                        category: category, month: month
                    },
                    url: "../Login/GetMonthlyDigest",
                    success:
                function (result) {
                    $("#rightmenu").empty();
                    $("#rightmenu").html(result);
                },
                error: function (res) {
                    AjaxFailure(res);
                }
            });
        }
        });
    $("#alphabut button").each(function () {
        if ($(this).text() === "A") {
            $(this).addClass('selectedTD');
        }
    });
                
                
    $(".article_alpha_Btn button").each(function () {
        // debugger;
        $(this).removeClass('selectedTD');
                 
    });

    //$('.navbar-nav li').click(function () {
    //    $('.navbar-nav li').find('.active').removeClass('active');
    //    $(this).addClass('active');
    //    alert("hi");
    //});
    $('.search_main_div').keypress(function (e) {
        //$("#menu-main-menu li").removeClass("active");
        //$("#home_navbar").addClass('active');

        if (e.which == 13) {
            $('.caseLaw').click();
        }
    });

    $('.searchButton').click(function () {
        //$("#menu-main-menu li").removeClass("active");
        //$("#home_navbar").addClass('active');
        
        textField();
        $('.searchButton').parent().find('.slectedButton').css('background-color', '#00a53c')
        $('.searchButton').parent().find('.slectedButton').removeClass('slectedButton');
        $(this).addClass('slectedButton');
        // $(this).css('background-color', '#366bff');

        if ($(this).attr('searchtype') == 'statutes') {
            //debugger;
            $('#caseLAwErrorNotifier').hide();
            clearSearchField();
            $('.search_main_div').show();
            $('.advanceSearchDiv').hide();
            $('.citationSearchDiv').hide();
            $('#citationCategory').hide();
            $('#caseLawYear').hide();
            $('#searchLabel').text('Statues Search');
            $('#yearSearch').hide();
            $('#courtSearch').hide();
            $('#codeOrPageSearch').hide();
            $('#bookSearch').show();
            $('.quad-input').find('.form-control').css('width', '100%');
            $('#bookSearch').attr('placeholder', 'Enter Year or Name of Statute');
            loadStatutesCharA();
            $("#bookSearch").typeahead('destroy');
            //$("#bookSearch").autocomplete({ source: [] });
            $("#menu-main-menu li").removeClass("active");
            $('#bookSearch').css("float", "left");
            $('#yearSearch').css("float", "left");
        }
        else if ($(this).attr('searchtype') == 'courtwise') {
            clearSearchField();
            $('#caseLAwErrorNotifier').hide();
            $('.search_main_div').show();
            $('.citationSearchDiv').hide();
            $('.advanceSearchDiv').hide();
            $('#citationCategory').hide();
            $('#searchLabel').text('Court Wise Search');
            $('#courtSearch').show();
            $('#bookSearch').show();
            $('#caseLawYear').hide();
            $('#codeOrPageSearch').hide();
            $('#bookSearch').attr('placeholder', 'Enter Book Name');
            $('#bookSearch').css("float", "right");
            $('#yearSearch').css("float", "right");
            $('#yearSearch').attr('placeholder', 'Enter Year (required)');
            var date12 = new Date();
            var intYear = date12.getFullYear() ;
            $('#yearSearch').val(intYear);
            $('#yearSearch').show();
            $("#bookSearch").typeahead({
                source: books
            });
            $('.quad-input').find('.form-control').css('width', '37.4%');
            $('#yearSearch').css('width', '25%');
            $('#courtSearch').attr('placeholder', 'Enter Court Name');

        }
        else if ($(this).attr('searchtype') == 'caselaw') {
            clearSearchField();
            $('#caseLAwErrorNotifier').hide();
            $('.search_main_div').show();
            $('.citationSearchDiv').hide();
            $('#citationCategory').hide();
            $('.advanceSearchDiv').hide();
            $('#searchLabel').text('Case Law Search');
            $('#yearSearch').hide();
            $('#courtSearch').show();
            $('#caseLawYear').show();
            $('#codeOrPageSearch').hide();
            $('#bookSearch').show();
            $('.quad-input').find('.form-control').css('width', '33%');
            $('#bookSearch').css('width', '47%');
            $('#caseLawYear').css('width', '20%');
            $('#bookSearch').css("float", "left");
            $('#yearSearch').css("float", "left");
            $('#bookSearch').attr('placeholder', 'Enter Keyword');
            $("#bookSearch").typeahead('destroy');

        }
        else if ($(this).attr('searchtype') == 'citation') {

            clearSearchField();
            $('#caseLAwErrorNotifier').hide();
            $('.search_main_div').hide();
            $('.citationSearchDiv').show();
            $('#Index_Court_Search_input').typeahead({
                source: courts
            });
            $('#Citation_Court_Search_input').typeahead({
                source: courts
            });
            $('#citationYearErrorNotifier').hide();
            $('.advanceSearchDiv').hide();
            //$('#btn_hide_on_Citation').hide();
            //$('.quad-input').find('.form-control').css('width', '25%');
            //$('#codeOrPageSearch').css({"border-right":"1px solid #ddd", "width":"16.2%"});
            //$('#Citation_Advance_Search_div').show();
            //$('#searchLabel').text('Citation Search');
            //$('#yearSearch').show();
            //$('#courtSearch').show();
            //$('#codeOrPageSearch').show();
            //$('#caseLawYear').hide();
            //$('#citationCategory').show();
            //$("#citationCategory option:selected").removeAttr("selected");
            ////$('#citationCategory').css('width', '10%')
            ////$('#yearSearch').css('width', '15%');
            //$('#yearSearch').attr('placeholder', 'Enter Year YYYY');
            //$('#bookSearch').hide();
            ////$('#bookSearch').attr('placeholder', 'Enter Category');
            //$('#courtSearch').attr('placeholder', 'Enter Court');
            //$('#codeOrPageSearch').attr('placeholder', 'Enter Code or Page#');
            //$('#bookSearch').css("float", "left");
            //$('#yearSearch').css("float", "left");
        }
        else if ($(this).attr('searchtype') == 'article') {
            $('.search_main_div').show();
            $('#caseLAwErrorNotifier').hide();
            $('.citationSearchDiv').hide();
            $('#citationCategory').hide();
            $('.advanceSearchDiv').hide();
            $("#bookSearch").typeahead('destroy');
            clearSearchField();
            $('#searchLabel').text('Article Search');
            $('#yearSearch').hide();
            $('#courtSearch').hide();
            $('#caseLawYear').hide();
            $('#codeOrPageSearch').hide();
            $('#bookSearch').show();
            $('.quad-input').find('.form-control').css('width', '100%');
            $('#bookSearch').attr('placeholder', 'Enter Title, Author, Year or Free text');
            $('#bookSearch').css("float", "left");
            $('#yearSearch').css("float", "left");
        }
        else if ($(this).attr('searchtype') == 'advance') {
            $('.search_main_div').hide();
            $('#caseLAwErrorNotifier').hide();
            $('.citationSearchDiv').hide();
            $('.advanceSearchDiv').show();
            $('#Advance_Court_Name_Search_input').typeahead({
                source: courts
            });
        }
        //jqUpdateSize();
    });
}catch(ex){}
});
function newStatueSearch(category) {
    try {
        $.ajax({
            type: 'POST',
            data: {
                category: category
            },
            url: "../Login/GetNewStatue",
            success:
        function (result) {
            $("#rightmenu").empty();
            $("#rightmenu").html(result);
            $(".statuebackButton").attr("searchtype", "new");
            $(".statuebackButton").attr("searchvalue", category);
        },
        error: function (res) {
            AjaxFailure(res);
        }
    });
} catch (ex) {

}
}
$(document).ready(function () {
    try {
        $('#citation_search_content').keypress(function (e) {
            //$("#menu-main-menu li").removeClass("active");
            //$("#home_navbar").addClass('active');

            if (e.which == 13) {
                $('.Citation_Search_btn').click();
            }
        });
        $('.Citation_Search_btn').click(function () {
            //debugger;
            var year = null;
            var book = null;
            var code = null;
            var court = null, judge = null, lawyer = null, party = null;
            book = $('#Citation_Category_Search_dropdown').val();
            year = $('#Citation_Year_Search_input').val();
            court = $('#Citation_Court_Search_input').val();
            code = $('#Citation_Code_Or_Page_Search_input').val();
            judge = $('#Citation_Judge_Search_input').val();
            lawyer = $('#Citation_Lawyer_Search_input').val();
            party = $('#Citation_Party_Search_input').val();
            if (!jQuery.trim(year).length > 0) {
                $('#citationYearErrorNotifier').show();
                return false;
            }
            if (!$.isNumeric(year)) {
                $('#citationYearErrorNotifier').show();
                return false;
            }
            $('#citationYearErrorNotifier').hide();
            $.ajax({
                type: 'POST',
                data: {
                    year: year, book: book, code: code, court: court, judge: judge, lawyer: lawyer, party: party
                },
                url: "../Login/CitationSearch",

                success: function (result) {

                    $("#rightmenu").empty();

                    $("#rightmenu").html(result);


                },
            error: function (res) {

                AjaxFailure(res);
            }
        });
    });

    $('#index_search_content').keypress(function (e) {
        //$("#menu-main-menu li").removeClass("active");
        //$("#home_navbar").addClass('active');

        if (e.which == 13) {
            $('.Index_Search_btn').click();
        }
    });
    $('.Index_Search_btn').click(function () {
        var year = null;
        var book = null;
        var court = null;
        book = $('#Index_Category_Search_dropdown').val();
        year = $('#Index_Year_Search_input').val();
        court = $('#Index_Court_Search_input').val();
        if (!jQuery.trim(year).length > 0) {
            $('#indexYearErrorNotifier').show();
            return false;
        }
        if (!$.isNumeric(year)) {
            $('#indexYearErrorNotifier').show();
            return false;
        }
        $('#indexYearErrorNotifier').hide();
        $.ajax({
            type: 'POST',
            data: {
                year: year, book: book, court: court
            },
            url: "../Login/IndexSearch",

            success: function (result) {

                $("#rightmenu").empty();

                $("#rightmenu").html(result);


            },
        error: function (res) {

            AjaxFailure(res);
        }
    });
});
} catch (ex) { }
});
//function that loads statutes from 1305-1324
function loadStatutesCharA(category) {
    try {
        $.ajax({
            type: 'POST',
            data: {
                category: category
            },
            url: "../Login/StatuecharASearch",
            success:
        function (result) {
            $("#rightmenu").empty();
            $("#rightmenu").html(result);
        },
        error: function (res) {
            AjaxFailure(res);
        }
    });
} catch (ex) {

}
}
function clearSearchField() {
    try {
        $('#btn_hide_on_Citation').show();
        $('#Citation_Advance_Search_div').hide();
        $('#yearSearch').val("");
        $('#courtSearch').val("");
        $('#codeOrPageSearch').val("");
        $('#bookSearch').val("");
        $("#Index_Category_Search_dropdown option:selected").removeAttr("selected");
        var date12 = new Date();
        var intYear = date12.getFullYear() ;
        $('#Index_Year_Search_input').val(intYear);
        $('#Index_Court_Search_input').val("");
        $('#Citation_Category_Search_dropdown option:selected').removeAttr("selected");
        $('#Citation_Year_Search_input').val(intYear);
        $('#Citation_Court_Search_input').val("");
        $('#Citation_Code_Or_Page_Search_input').val("");
        $('#Citation_Judge_Search_input').val("");
        $('#Citation_Lawyer_Search_input').val("");
        $('#Citation_Party_Search_input').val("");
    } catch (ex) {

    }
}
//$('body').bind('copy paste', function (e) {
//    e.preventDefault(); return false;
//});


$(document).on("click", "#menu-main-menu li", function () {
    try {
        $("#menu-main-menu li").removeClass("active");
        $(this).addClass('active');
    } catch (ex) {

    }
});

$(document).mouseup(function (e) {
    try {
        var container = new Array();
        container.push($('#popupBottom'));
        //container.push($('#item_2'));

        $.each(container, function (key, value) {
            if (!$(value).is(e.target) // if the target of the click isn't the container...
                && $(value).has(e.target).length === 0) // ... nor a descendant of the container
            {
                $(value).hide();
            }
        });
    } catch (ex) { }
});
$(document).ajaxStart(function () {
    $('.modalbookmarklogo').html("Bookmark this Case <span class='glyphicon glyphicon-bookmark' style='font-size: 14px; top: 3px'></span>");
    $("#loadingScreen").css("display", "block");

});
$(document).ajaxComplete(function () {
            
    $('.case_description_modal_body').scrollTop(0);
    $("#loadingScreen").css("display", "none");
});



        $(document).ready(function () {
            try {
                $('#pop').click(function () {
                    // $(this).children().append($("#popupBottom"));
                    var pos = $(this).position();

                    // .outerWidth() takes into account border and padding.
                    var width = $(this).outerWidth();

                    //show the menu directly over the placeholder
                    $("#popupBottom").css({
                        //position: "absolute",
                        //  top: pos.top + 42 + "px",
                        // left: (pos.left - width - 10) + "px"
                    }).show();

                });



                $('.modalbookmarklogo').click(function () {
                    //debugger;
                    var caseName = $(this).attr('modalCaseName');
                   
                    var currElem = $(this);
					var searchType = $.trim(String($('#bookSearch').val())).replace('<','"').replace('>','"');
					//console.log("over here",searchType)
					//return false;
                    $.ajax({
                        type: 'POST',
                        url: "../Login/SaveBookMark",
                        data: { caseName: caseName, searchType:  searchType},
                    success: function (result) {
                        $(currElem).text("Bookmarked");
                        //$("#modalbookmarmessage").text("Bookmarked");
                        //setTimeout(function () { $('#modalbookmarmessage').text(""); }, 1000);

                    }

                });
                    
            });
        } catch (ex) { }
});
function setCharAt(str, index, chr) {
    try {
        if (index > str.length - 1) return str;
        return str.substr(0, index) + chr + str.substr(index + 1);
    } catch (ex) { }
}
$(document).ready(function () {
    try {
        var years = [];
        var d = new Date("July 21, 1949 01:15:00");
        var n = d.getFullYear();

        for (var i = n ; i <= new Date().getFullYear() ; i++) {
            years.push(i.toString());

        }

        $('#courtSearch').typeahead({
            source: courts
        });
        $('#yearSearch').typeahead({
            source: years
        });


        $(".caseLaw").click(function () {
            // debugger;
            var searchType = $('.searchButton').parent().find('.slectedButton').attr('searchType');
            var year = null;
            var book = null;
            var code = null;
            var court = null, judge = null, lawyer = null, party = null;
            if ($('#bookSearch').val().trim() != '') {
                book = $('#bookSearch').val().trim();
            }
            if (searchType == "caselaw") {
                //debugger;
                book = $('#bookSearch').val().trim();
                if (book.indexOf("[") >= 0 || book.indexOf("]") >= 0) {
                    var countopeningbrackets = 0;
                    var countclosingbrackets = 0;
                    for (var i = 0; i < book.length; i++) {
                        if (book[i] == '[') {
                            countopeningbrackets++;

                        }
                        if (book[i] == ']') {
                            if (countclosingbrackets + 1 != countopeningbrackets) {
                                $('#caseLAwErrorNotifier').show();
                                return false;
                            }
                            countclosingbrackets++;
                        }
                    }
                    if (countopeningbrackets != countclosingbrackets) {
                        $('#caseLAwErrorNotifier').show();
                        return false;
                    }

                }
                if (book.indexOf('\"') >= 0) {
                    var count = 0;
                    for (var i = 0; i < book.length; i++) {
                        if (book[i] == '\"') {
                            count++;
                            if (count % 2 == 0) {
                                // book[i] = ']';
                                book = setCharAt(book, i, ']');
                            }
                            if (count % 2 != 0) {
                                //book[i] = '[';
                                // book = book.replaceAt(i, "");
                                book = setCharAt(book, i, '[');
                            }
                        }
                    }
                    if (count % 2 != 0) {
                        $('#caseLAwErrorNotifier').show();
                        return false;
                    }

                }

                if (book.indexOf("<") >= 0 || book.indexOf(">") >= 0) {
                    var countopeningbrackets = 0;
                    var countclosingbrackets = 0;
                    for (var i = 0; i < book.length; i++) {
                        if (book[i] == '<') {
                            countopeningbrackets++;

                        }
                        if (book[i] == '>') {
                            if (countclosingbrackets + 1 != countopeningbrackets) {
                                $('#caseLAwErrorNotifier').show();
                                return false;
                            }
                            countclosingbrackets++;
                        }
                    }
                    if (countopeningbrackets != countclosingbrackets) {
                        $('#caseLAwErrorNotifier').show();
                        return false;
                    }
                    else {
                        book = book.replace(/</g, "[");
                        book = book.replace(/>/g, "]");
                    }
                }

            }
            if (searchType == "courtwise") {
                //debugger;
                year = $('#yearSearch').val().trim();
                if (!jQuery.trim(year).length > 0) {
                    $('#courtwiseYearErrorNotifier').show();
                    return false;
                }
                if (!$.isNumeric(year)) {
                    $('#courtwiseYearErrorNotifier').show();
                    return false;
                }
            }
            $('#courtwiseYearErrorNotifier').hide();
            $('#caseLAwErrorNotifier').hide();
            if ($('#yearSearch').val().trim() != '') {
                year = $('#yearSearch').val().trim();
            }
            if (year == '' && searchType == "caselaw") {
                var currentTime = new Date();
                year = currentTime.getFullYear() - 5;
            }

            if ($('#codeOrPageSearch').val().trim() != '') {
                code = $('#codeOrPageSearch').val().trim();
            }
            if ($('#courtSearch').val().trim() != '') {
                court = $('#courtSearch').val().trim();
            } if ($('#judgeSearch').val().trim() != '') {
                judge = $('#judgeSearch').val().trim();
            }
            if ($('#lawyerSearch').val().trim() != '') {
                lawyer = $('#lawyerSearch').val().trim();
            }
            if ($('#partySearch').val().trim() != '') {
                party = $('#partySearch').val().trim();
            }
           // debugger;
            var currCaseTypeId = $('#statuteCaseTypeId').val();
            if (currCaseTypeId !== undefined) {
                
                
                var searchType = $(".statuteLawBackButton").attr("searchType");
                var searchValue = $(".statuteLawBackButton").attr("searchValue");
                var searchChar = $(".statuteLawBackButton").attr("searchChar");
                var statueName = $('.statuteResult').text();
                $.ajax({
                    type: 'POST',
                    data: {
                        book: book, book: book, caseTypeId: currCaseTypeId, court: court
                    },
                    url: "../Login/searchStatuteCaseLaw",

                    success: function (result) {

                        $("#rightmenu").empty();
                        $("#rightmenu").html(result);
                        $(".statuteLawBackButton").attr("searchType", searchType);
                        $(".statuteLawBackButton").attr("searchValue", searchValue);
                        $(".statuteLawBackButton").attr("searchChar", searchChar);
                        $(".statuteLawBackButton").show();
                        $('.statuteResult').text(statueName);
                    },
                    error: function (res) {

                        AjaxFailure(res);
                    }
                });
            } else {

            
            $.ajax({
                type: 'POST',
                data: {
                    year: year, book: book, code: code, court: court, searchType: searchType, judge: judge, lawyer: lawyer, party: party
                },
                url: "../Login/SearchCaseLaw",

                success: function (result) {

                    $("#rightmenu").empty();
                    $("#rightmenu").html(result);
                    if (searchType == "statutes") {
                        $("#alphabut button").each(function () {

                            $(this).removeClass('selectedTD');



                        });
                    }


                    if (searchType == 'caselaw') {
                        $('.readMore').css("display", "block");
                    }
                },
            error: function (res) {

                AjaxFailure(res);
            }
            });
            }
    });
} catch (ex) { }
});





        //$(".readMore").unbind("click");

var pageSize = 5;
var pageIndex = 0;
$(document).ready(function () {
    try {
        $('.readMore').click(function () {
            LoadMoreCaseLaw();

        });

    } catch (ex) { }
});

function LoadMoreCaseLaw() {
    //debugger;
    try {
        var rec = $('#caseLawRowNo').val();
        var row = parseInt(rec);
        var court = $('#bookName').attr('court-name');
        var book = $('#bookName').attr('book-name');
        var year = 2011;

        var caseTypeId = $('#caseTypeId').val();
        debugger;
        if (caseTypeId !== undefined) {
            //caseTypeId = 0;
        }
        else {
            caseTypeId = $('#statuteCaseTypeId').val();
            //statuteCaseTypeId
            if (caseTypeId == undefined) {
                caseTypeId = 0;
            }
        }
        var currentTime = new Date();
        year = currentTime.getFullYear() - 5;

        row += 50;
        if ($('#caseLawYear').val().trim() != '') {
            year = $('#caseLawYear').val().trim();
            year = currentTime.getFullYear() - year;
        }

        //if ($('#bookSearch').val().trim() != '') {
        //    book = $('#bookSearch').val().trim();
        //}
        //if ($('#courtSearch').val().trim() != '') {
        //    court = $('#courtSearch').val().trim();
        //}
        $.ajax({

            type: 'GET',
            url: "../Login/LoadMoreCaseLaw",
            data: { book: book, court: court, row: row, year: year, caseTypeId: caseTypeId },
        //dataType: 'json',
        success: function (result) {

            //$("#mainContent").empty();
            if (result != "-1") {

                $("#rightmenu").append(result);
                $('#caseLawRowNo').val(row);
            } else {

                $('.readMore').hide();
            }

        },
        beforeSend: function () {
            $("#loading").css("display", "block");
            //  $(".windows8").show();
        },
        complete: function () {
            //$("html, body").animate({ scrollTop: 0 }, "slow");
            $("#loading").css("display", "none");
        },
        error: function () {
            alert("Error while retrieving data!");
        }
    });
} catch (Ex) { }
}
function highlightSearch() {
    try {
        var text = document.getElementById('query').value;
        if (text != "") {
            var query = new RegExp("(\\b" + text + "\\b)", "gim");
            var e = document.getElementById("searchtext").innerHTML;
            var enew = e.replace(/(<span>|<\/span>)/igm, "");
            document.getElementById("searchtext").innerHTML = enew;
            var newe = enew.replace(query, "<span>$1</span>");
            document.getElementById("searchtext").innerHTML = newe;
        }
    } catch (ex) { }
}

function GetData() {
    try {
        var year = '';
        var book = '';
        var code = '';
        var court = '';
        pageIndex++;
        if ($('#yearSearch').val().trim() != '') {
            year = $('#yearSearch').val().trim();
        }
        if ($('#bookSearch').val().trim() != '') {
            book = $('#bookSearch').val().trim();
        }
        if ($('#codeOrPageSearch').val().trim() != '') {
            code = $('#codeOrPageSearch').val().trim();
        }
        if ($('#courtSearch').val().trim() != '') {
            court = $('#courtSearch').val().trim();
        }
        var searchType = $('.searchButton').parent().find('.slectedButton').attr('searchType');
        if (searchType == "caselaw") {
            LoadMoreCaseLaw();
            return false;
        }
        $.ajax({

            type: 'GET',
            url: "../Login/SearchCaseLaw",
            data: {
            pageindex: pageIndex, pagesize: pageSize, year: year, book: book, code: code, court: court, searchType: searchType
            },
        success: function (result) {
            //debugger;
            if (result != null) {

                $("#rightmenu").append(result);
            }
            else {
                $('.readMore').css("display", "none");
            }
        },
        beforeSend: function () {
            $("#loading").css("display", "block");
            //  $(".windows8").show();
        },
        complete: function () {
            //$("html, body").animate({ scrollTop: 0 }, "slow");
            $("#loading").css("display", "none");
        },
        error: function () {
            alert("Error while retrieving data!");
        }
    });
} catch (ex) { }
}

    function disableselect(e) {
        return false
    }
function reEnable() {
    return true
}
document.onselectstart = new Function("return false")
if (window.sidebar) {
    document.onmousedown = disableselect
    document.onclick = reEnable
}



        //////////F12 disable code////////////////////////
            document.onkeypress = function (event) {
                event = (event || window.event);
                if (event.keyCode == 123) {
                    //alert('No F-12');
                    return false;
                }
            }
document.onmousedown = function (event) {
    event = (event || window.event);
    if (event.keyCode == 123) {
        //alert('No F-keys');
        return false;
    }
}
document.onkeydown = function (event) {
    event = (event || window.event);
    if (event.keyCode == 123) {
        //alert('No F-keys');
        return false;
    }
}
/////////////////////end///////////////////////



var message="Sorry, right-click has been disabled";
///////////////////////////////////
function clickIE() {if (document.all) {(message);return false;}}
function clickNS(e) {if
(document.layers||(document.getElementById&&!document.all)) {
    if (e.which==2||e.which==3) {(message);return false;}}}
if (document.layers)
{document.captureEvents(Event.MOUSEDOWN);document.onmousedown=clickNS;}
else{document.onmouseup=clickNS;document.oncontextmenu=clickIE;}
document.oncontextmenu=new Function("return false")
//
function disableCtrlKeyCombination(e)
{
    //list all CTRL + key combinations you want to disable
    var forbiddenKeys = new Array('a', 'n', 'c', 'x', 'v', 'j' , 'w');
    var key;
    var isCtrl;
    if(window.event)
    {
        key = window.event.keyCode;     //IE
        if(window.event.ctrlKey)
            isCtrl = true;
        else
            isCtrl = false;
    }
    else
    {
        key = e.which;     //firefox
        if(e.ctrlKey)
            isCtrl = true;
        else
            isCtrl = false;
    }
    //if ctrl is pressed check if other key is in forbidenKeys array
    if(isCtrl)
    {
        for(i=0; i<forbiddenKeys.length; i++)
        {
            //case-insensitive comparation
            if(forbiddenKeys[i].toLowerCase() == String.fromCharCode(key).toLowerCase())
            {
                alert('Key combination CTRL + '+String.fromCharCode(key) +' has been disabled.');
                return false;
            }
        }
    }
    return true;
}
