/**
 * Tagify
 */

'use strict';
let TagifyUserList;
let button;
let get_usersList_tag = [];

(function () {

    // Basic
    //------------------------------------------------------
    const tagifyBasicEl = document.querySelector('#TagifyBasic');
    //const TagifyBasic = new Tagify(tagifyBasicEl);

    // Read only
    //------------------------------------------------------
    const tagifyReadonlyEl = document.querySelector('#TagifyReadonly');
    //const TagifyReadonly = new Tagify(tagifyReadonlyEl);

    // Custom list & inline suggestion
    //------------------------------------------------------
    const TagifyCustomInlineSuggestionEl = document.querySelector('#TagifyCustomInlineSuggestion');
    const TagifyCustomListSuggestionEl = document.querySelector('#TagifyCustomListSuggestion');

    const whitelist = [
        'A# .NET',
        'A# (Axiom)',
        'A-0 System',
        'A+',
        'A++',
        'ABAP',
        'ABC',
        'ABC ALGOL',
        'ABSET',
        'ABSYS',
        'ACC',
        'Accent',
        'Ace DASL',
        'ACL2',
        'Avicsoft',
        'ACT-III',
        'Action!',
        'ActionScript',
        'Ada',
        'Adenine',
        'Agda',
        'Agilent VEE',
        'Agora',
        'AIMMS',
        'Alef',
        'ALF',
        'ALGOL 58',
        'ALGOL 60',
        'ALGOL 68',
        'ALGOL W',
        'Alice',
        'Alma-0',
        'AmbientTalk',
        'Amiga E',
        'AMOS',
        'AMPL',
        'Apex (Salesforce.com)',
        'APL',
        'AppleScript',
        'Arc',
        'ARexx',
        'Argus',
        'AspectJ',
        'Assembly language',
        'ATS',
        'Ateji PX',
        'AutoHotkey',
        'Autocoder',
        'AutoIt',
        'AutoLISP / Visual LISP',
        'Averest',
        'AWK',
        'Axum',
        'Active Server Pages',
        'ASP.NET'
    ];
    // Inline
    // let TagifyCustomInlineSuggestion = new Tagify(TagifyCustomInlineSuggestionEl, {
    //   whitelist: whitelist,
    //   maxTags: 10,
    //   dropdown: {
    //     maxItems: 20,
    //     classname: 'tags-inline',
    //     enabled: 0,
    //     closeOnSelect: false
    //   }
    // });
    // List
    // let TagifyCustomListSuggestion = new Tagify(TagifyCustomListSuggestionEl, {
    //   whitelist: whitelist,
    //   maxTags: 10,
    //   dropdown: {
    //     maxItems: 20,
    //     classname: '',
    //     enabled: 0,
    //     closeOnSelect: false
    //   }
    // });

    // Users List suggestion
    //------------------------------------------------------


    const TagifyUserListEl = document.querySelector('#TagifyUserList');

// 사용자 정보를 가져오는 비동기 함수
    async function fetchData() {
        try {
            const response = await fetch('/admins/member_info/');
            const userData = await response.json();
            // console.log('user', userData);
            userData.user_data.sort((a, b) => {
                if (a.fields.department_position === b.fields.department_position) {
                    // department_position이 같은 경우 job_position으로 정렬
                    return a.fields.job_position - b.fields.job_position;
                }
                // department_position으로 정렬
                return a.fields.department_position - b.fields.department_position;
            });
            const get_usersList_tag = userData.user_data.map(user => ({
                value: user.pk,
                name: user.fields.username,
                avatar: userData.code_data.find(code => code.pk === user.fields.department_position).fields.name,
                email: userData.code_data.find(code => code.pk === user.fields.job_position).fields.name
            }));
            // console.log('usersList', get_usersList_tag);
            TagifyUserList.settings.whitelist = get_usersList_tag;
            TagifyUserList.update();
        } catch (error) {
            // console.error('Error fetching users list:', error);
        }
    }

// fetchData 함수 호출
    fetchData();

    // const usersList = [
    //   {
    //     value: 1,
    //     name: 'Justinian Hattersley',
    //     avatar: 'https://i.pravatar.cc/80?img=1',
    //     email: 'jhattersley0@ucsd.edu'
    //   },
    //   {
    //     value: 2,
    //     name: 'Antons Esson',
    //     avatar: 'https://i.pravatar.cc/80?img=2',
    //     email: 'aesson1@ning.com'
    //   },
    //   {
    //     value: 3,
    //     name: 'Ardeen Batisse',
    //     avatar: 'https://i.pravatar.cc/80?img=3',
    //     email: 'abatisse2@nih.gov'
    //   },
    //   {
    //     value: 4,
    //     name: 'Graeme Yellowley',
    //     avatar: 'https://i.pravatar.cc/80?img=4',
    //     email: 'gyellowley3@behance.net'
    //   },
    //   {
    //     value: 5,
    //     name: 'Dido Wilford',
    //     avatar: 'https://i.pravatar.cc/80?img=5',
    //     email: 'dwilford4@jugem.jp'
    //   },
    //   {
    //     value: 6,
    //     name: 'Celesta Orwin',
    //     avatar: 'https://i.pravatar.cc/80?img=6',
    //     email: 'corwin5@meetup.com'
    //   },
    //   {
    //     value: 7,
    //     name: 'Sally Main',
    //     avatar: 'https://i.pravatar.cc/80?img=7',
    //     email: 'smain6@techcrunch.com'
    //   },
    //   {
    //     value: 8,
    //     name: 'Grethel Haysman',
    //     avatar: 'https://i.pravatar.cc/80?img=8',
    //     email: 'ghaysman7@mashable.com'
    //   },
    //   {
    //     value: 9,
    //     name: 'Marvin Mandrake',
    //     avatar: 'https://i.pravatar.cc/80?img=9',
    //     email: 'mmandrake8@sourceforge.net'
    //   },
    //   {
    //     value: 10,
    //     name: 'Corrie Tidey',
    //     avatar: 'https://i.pravatar.cc/80?img=10',
    //     email: 'ctidey9@youtube.com'
    //   }
    // ];

    function tagTemplate(tagData) {
        return `
        <tag title="${tagData.title || tagData.email}"
          contenteditable='false'
          spellcheck='false'
          tabIndex="-1"
          class="${this.settings.classNames.tag} ${tagData.class ? tagData.class : ''}"
          ${this.getAttributes(tagData)}
        >
          <x title='' class='tagify__tag__removeBtn' role='button' aria-label='remove tag'></x>
          <div>
            <div class='tagify__tag__avatar-wrap'>
              <i class='bx bxs-user-circle'></i>
            </div>
            <span class='tagify__tag-text'>${tagData.avatar} ${tagData.name} ${tagData.email}</span>
          </div>
        </tag>
      `;
    }

    function suggestionItemTemplate(tagData) {
        // console.log('tagData', tagData)
        return `
        <div ${this.getAttributes(tagData)}
          class='tagify__dropdown__item align-items-center ${tagData.class ? tagData.class : ''}'
          tabindex="0"
          role="option">
          ${tagData.avatar
            ? `<div class='tagify__dropdown__item__avatar-wrap'>
                 <i class='bx bxs-user-circle' style='font-size: 36px;'></i>
               </div>`
            : ''}
          <div class="fw-medium" style="margin-top: 5px;">${tagData.avatar} ${tagData.name} ${tagData.email}</div>
        </div>
      `;
    }

    function dropdownHeaderTemplate(suggestions) {
        return `
        <div class="${this.settings.classNames.dropdownItem} ${this.settings.classNames.dropdownItem}__addAll">
            <strong>${this.value.length ? `Add remaning` : 'Add All'}</strong>
            <span>${suggestions.length} members</span>
        </div>
    `;
    }

    // initialize Tagify on the above input node reference
    let TagifyUserList = new Tagify(TagifyUserListEl, {
        tagTextProp: 'name', // very important since a custom template is used with this property as text. allows typing a "value" or a "name" to match input with whitelist
        enforceWhitelist: true,
        skipInvalid: true, // do not remporarily add invalid tags
        dropdown: {
            closeOnSelect: false,
            enabled: 0,
            classname: 'users-list',
            searchKeys: ['name', 'email'], // very important to set by which keys to search for suggesttions when typing
            maxItems: 100
        },
        templates: {
            tag: tagTemplate,
            dropdownItem: suggestionItemTemplate,
            dropdownHeader: dropdownHeaderTemplate
        },
        whitelist: get_usersList_tag
    });

    // attach events listeners
    TagifyUserList.on('dropdown:select', onSelectSuggestion) // allows selecting all the suggested (whitelist) items
        .on('edit:start', onEditStart); // show custom text in the tag while in edit-mode

    function onSelectSuggestion(e) {
        // custom class from "dropdownHeaderTemplate"
        if (e.detail.elm.classList.contains(`${TagifyUserList.settings.classNames.dropdownItem}__addAll`))
            TagifyUserList.dropdown.selectAll();
    }

    function onEditStart({detail: {tag, data}}) {
        TagifyUserList.setTagTextNode(tag, `${data.name} <${data.email}>`);
    }

    // Email List suggestion
    //------------------------------------------------------
    // generate random whitelist items (for the demo)
    let randomStringsArr = Array.apply(null, Array(100)).map(function () {
        return (
            Array.apply(null, Array(~~(Math.random() * 10 + 3)))
                .map(function () {
                    return String.fromCharCode(Math.random() * (123 - 97) + 97);
                })
                .join('') + '@gmail.com'
        );
    });

    const TagifyEmailListEl = document.querySelector('#TagifyEmailList'),
      // TagifyEmailList = new Tagify(TagifyEmailListEl, {
      //   // email address validation (https://stackoverflow.com/a/46181/104380)
      //   pattern:
      //     /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
      //   whitelist: randomStringsArr,
      //   callbacks: {
      //     invalid: onInvalidTag
      //   },
      //   dropdown: {
      //     position: 'text',
      //     enabled: 1 // show suggestions dropdown after 1 typed character
      //   }
      // }),


    button = TagifyUserListEl.nextElementSibling; // "add new tag" action-button

    //button.addEventListener('click', onAddButtonClick);

    // function onAddButtonClick() {
    //   TagifyEmailList.addEmptyTag();
    // }

    function onInvalidTag(e) {
        console.log('invalid', e.detail);
    }
})();
