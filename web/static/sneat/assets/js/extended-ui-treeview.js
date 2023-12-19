/**
 * Treeview (jquery)
 */

'use strict';

$(function () {
  var theme = $('html').hasClass('light-style') ? 'default' : 'default-dark',
    basicTree = $('#jstree-basic'),
    customIconsTree = $('#jstree-custom-icons'),
    contextMenu = $('#jstree-context-menu'),
    dragDrop = $('#jstree-drag-drop'),
    checkboxTree = $('#jstree-checkbox'),
    ajaxTree = $('#jstree-ajax');

  // Basic
  // --------------------------------------------------------------------
  if (basicTree.length) {
    basicTree.jstree({
      core: {
        themes: {
          name: theme
        }
      }
    });
  }

  // Custom Icons
  // --------------------------------------------------------------------
  if (customIconsTree.length) {
    customIconsTree.jstree({
      core: {
        themes: {
          name: theme
        },
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Context Menu
  // --------------------------------------------------------------------
  if (contextMenu.length) {
    contextMenu.jstree({
      core: {
        themes: {
          name: theme
        },
        check_callback: true,
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types', 'contextmenu'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Drag Drop
  // --------------------------------------------------------------------
  if (dragDrop.length) {
    dragDrop.jstree({
      core: {
        themes: {
          name: theme
        },
        check_callback: true,
        data: [
          {
            text: 'css',
            children: [
              {
                text: 'app.css',
                type: 'css'
              },
              {
                text: 'style.css',
                type: 'css'
              }
            ]
          },
          {
            text: 'img',
            state: {
              opened: true
            },
            children: [
              {
                text: 'bg.jpg',
                type: 'img'
              },
              {
                text: 'logo.png',
                type: 'img'
              },
              {
                text: 'avatar.png',
                type: 'img'
              }
            ]
          },
          {
            text: 'js',
            state: {
              opened: true
            },
            children: [
              {
                text: 'jquery.js',
                type: 'js'
              },
              {
                text: 'app.js',
                type: 'js'
              }
            ]
          },
          {
            text: 'index.html',
            type: 'html'
          },
          {
            text: 'page-one.html',
            type: 'html'
          },
          {
            text: 'page-two.html',
            type: 'html'
          }
        ]
      },
      plugins: ['types', 'dnd'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }

  // Checkbox
  // --------------------------------------------------------------------
  $.ajax({
    url: "/admins/member_info/", // 사용자 정보를 제공하는 API의 URL
    method: "GET",
    dataType: "json",
    success: function(data) {
      console.log('member', data)

      // CodeMaster 데이터를 ID를 키로, name을 값으로 하는 객체로 변환
      var codeMasterMap = data.code_data.reduce(function (result, item) {
        result[item.pk] = item.fields.name;
        return result;
      }, {});

      // 사용자 데이터를 부서별로 그룹화
      var groupedData = data.user_data.reduce(function (result, user) {
        var departmentId = user.fields.department_position;
        if (!result[departmentId]) {
          result[departmentId] = [];
        }
        result[departmentId].push(user);
        return result;
      }, {});

      var treeData = [];

      console.log('codemaster : ',codeMasterMap);

// 각 그룹에 대해 폴더 노드를 만들고 사용자 노드를 추가
      for (var departmentId in groupedData) {
        var departmentUsers = groupedData[departmentId];

        // 폴더 노드 추가
        treeData.push({
          id: 'd_' + departmentId,
          parent: '#',
          text: codeMasterMap[departmentId] // 부서 이름으로 변환
        });

        // 사용자 노드 추가
        departmentUsers.forEach(function (user) {
          treeData.push({
            id: user.pk,
            parent: 'd_' + departmentId,
            text: user.fields.username + ' (' + codeMasterMap[name] + ')' // 직급 이름으로 변환
          });
        });
      }

      checkboxTree.jstree({
        core: {
          themes: {
            name: theme
          },
          data: treeData
        },
        plugins: ['types', 'checkbox', 'wholerow'],
        types: {
          default: {
            icon: 'bx bx-folder'
          },
          html: {
            icon: 'bx bxl-html5 text-danger'
          },
          css: {
            icon: 'bx bxl-css3 text-info'
          },
          img: {
            icon: 'bx bx-image text-success'
          },
          js: {
            icon: 'bx bxl-nodejs text-warning'
          }
        }
      });
    }
  })

  // if (checkboxTree.length) {
  //   checkboxTree.jstree({
  //     core: {
  //       themes: {
  //         name: theme
  //       },
  //       data: [
  //         {
  //           text: 'css',
  //           children: [
  //             {
  //               text: 'app.css',
  //               type: 'css'
  //             },
  //             {
  //               text: 'style.css',
  //               type: 'css'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'img',
  //           state: {
  //             opened: true
  //           },
  //           children: [
  //             {
  //               text: 'bg.jpg',
  //               type: 'img'
  //             },
  //             {
  //               text: 'logo.png',
  //               type: 'img'
  //             },
  //             {
  //               text: 'avatar.png',
  //               type: 'img'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'js',
  //           state: {
  //             opened: true
  //           },
  //           children: [
  //             {
  //               text: 'jquery.js',
  //               type: 'js'
  //             },
  //             {
  //               text: 'app.js',
  //               type: 'js'
  //             }
  //           ]
  //         },
  //         {
  //           text: 'index.html',
  //           type: 'html'
  //         },
  //         {
  //           text: 'page-one.html',
  //           type: 'html'
  //         },
  //         {
  //           text: 'page-two.html',
  //           type: 'html'
  //         }
  //       ]
  //     },
  //     plugins: ['types', 'checkbox', 'wholerow'],
  //     types: {
  //       default: {
  //         icon: 'bx bx-folder'
  //       },
  //       html: {
  //         icon: 'bx bxl-html5 text-danger'
  //       },
  //       css: {
  //         icon: 'bx bxl-css3 text-info'
  //       },
  //       img: {
  //         icon: 'bx bx-image text-success'
  //       },
  //       js: {
  //         icon: 'bx bxl-nodejs text-warning'
  //       }
  //     }
  //   });
  // }

  // Ajax Example
  // --------------------------------------------------------------------
  if (ajaxTree.length) {
    ajaxTree.jstree({
      core: {
        themes: {
          name: theme
        },
        data: {
          url: assetsPath + 'json/jstree-data.json',
          dataType: 'json',
          data: function (node) {
            return {
              id: node.id
            };
          }
        }
      },
      plugins: ['types', 'state'],
      types: {
        default: {
          icon: 'bx bx-folder'
        },
        html: {
          icon: 'bx bxl-html5 text-danger'
        },
        css: {
          icon: 'bx bxl-css3 text-info'
        },
        img: {
          icon: 'bx bx-image text-success'
        },
        js: {
          icon: 'bx bxl-nodejs text-warning'
        }
      }
    });
  }
});
