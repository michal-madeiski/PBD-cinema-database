//CINEMA
db.createCollection("cinema", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "cinema",
      "required": ["city", "street", "building_number", "region_name"],
      "properties": {
        "city": {
          "bsonType": "string"
        },
        "street": {
          "bsonType": "string"
        },
        "building_number": {
          "bsonType": "string"
        },
        "region_name": {
          "bsonType": "string"
        }
      },
      "patternProperties": {
        "rooms": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["room_number"],
            "properties": {
              "room_number": {
                "bsonType": "int"
              },
              "seats": {
                "bsonType": "array",
                "items": {
                  "title": "object",
                  "required": ["seat_number"],
                  "properties": {
                    "seat_number": {
                      "bsonType": "int"
                    }
                  }
                }  
              }
            }
          }  
        }
      }  
    } 
  }
});
//CINEMA

//DISCOUNT
db.createCollection("discount", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "discount",
      "required": ["name", "percentage"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "percentage": {
          "bsonType": "decimal"
        }
      }  
    } 
  }
});
//DISCOUNT

//GROUP_TYPE
db.createCollection("group_type", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "group_type",
      "required": ["name", "discount_percentage", "min_size"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "discount_percentage": {
          "bsonType": "decimal"
        },
        "min_size": {
          "bsonType": "int"
        }
      }  
    } 
  }
});
//GROUP_TYPE

//MOVIE
db.createCollection("movie", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "movie",
      "required": ["title", "director", "duration_minutes", "versions", "license"],
      "properties": {
        "title": {
          "bsonType": "string"
        },
        "director": {
          "bsonType": "string"
        },
        "duration_minutes": {
          "bsonType": "int"
        },
        "versions": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["language", "subtitles", "format"],
            "properties": {
              "language": {
                "bsonType": "string"
              },
              "subtitles": {
                "bsonType": "string"
              },
              "format": {
                "bsonType": "string"
              }
            }
          }  
        },
        "license": {
          "bsonType": "object",
          "title": "object",
          "required": ["number", "end_date", "start_date", "cost"],
          "properties": {
            "number": {
              "bsonType": "string"
            },
            "end_date": {
              "bsonType": "date"
            },
            "start_date": {
              "bsonType": "date"
            },
            "cost": {
              "bsonType": "decimal"
            }
          }  
        }
      }  
    } 
  }
});
//MOVIE

//ORDER
db.createCollection("order", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "order",
      "required": ["cinema_id", "status", "amount", "payment_type", "time_of_payment"],
      "properties": {
        "user_id": {
          "bsonType": "objectId"
        },
        "cinema_id": {
          "bsonType": "objectId"
        },
        "status": {
          "enum": ["reserved", "pending", "paid"]
        },
        "amount": {
          "bsonType": "decimal"
        },
        "time_of_payment": {
          "bsonType": "date"
        },
        "product_snapshot": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["name", "price", "count", "product_id"],
            "properties": {
              "name": {
                "bsonType": "string"
              },
              "price": {
                "bsonType": "decimal"
              },
              "count": {
                "bsonType": "int"
              },
              "product_id": {
                "bsonType": "objectId"
              }
            }
          }  
        },
        "payment_type": {
          "enum": ["blik", "cash", "card", "online", "voucher"]
        },
        "ticket": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["total_price", "qr_code", "status", "group_type_snapshot", "screening_id", "seats_snapshot", "movie_title"],
            "properties": {
              "total_price": {
                "bsonType": "decimal"
              },
              "qr_code": {
                "bsonType": "string"
              },
              "status": {
                "enum": ["valid", "used", "reserved", "not_used"]
              },
              "group_type_snapshot": {
                "bsonType": "object",
                "title": "object",
                "required": ["name", "discount_percentage", "_id"],
                "properties": {
                  "name": {
                    "bsonType": "string"
                  },
                  "discount_percentage": {
                    "bsonType": "decimal"
                  },
                  "_id": {
                    "bsonType": "objectId"
                  }
                }  
              },
              "screening_id": {
                "bsonType": "objectId"
              },
              "seats_snapshot": {
                "bsonType": "array",
                "items": {
                  "title": "object",
                  "required": ["seat_number", "ticket_type", "ticket_base_price", "ticket_type_id", "discount_name", "discount_id", "discount_percentage"],
                  "properties": {
                    "seat_number": {
                      "bsonType": "int"
                    },
                    "ticket_type": {
                      "bsonType": "string"
                    },
                    "ticket_base_price": {
                      "bsonType": "decimal"
                    },
                    "ticket_type_id": {
                      "bsonType": "objectId"
                    },
                    "discount_name": {
                      "bsonType": "string"
                    },
                    "discount_id": {
                      "bsonType": "objectId"
                    },
                    "discount_percentage": {
                      "bsonType": "decimal"
                    }
                  }
                }  
              },
              "special_offer_amount": {
                "bsonType": "decimal"
              },
              "special_offer_id": {
                "bsonType": "objectId"
              },
              "movie_title": {
                "bsonType": "string"
              }
            }
          }  
        }
      }  
    } 
  }
});
//ORDER

//PRODUCT
db.createCollection("product", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "product",
      "required": ["name", "barcode", "is_available", "price"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "barcode": {
          "bsonType": "string"
        },
        "is_available": {
          "bsonType": "bool"
        },
        "price": {
          "bsonType": "decimal"
        }
      }  
    } 
  }
});
//PRODUCT

//SCREENING
db.createCollection("screening", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "screening",
      "required": ["cinema_id", "start_time", "end_time", "movie_id", "movie_title", "version_snapshot", "room_number"],
      "properties": {
        "start_time": {
          "bsonType": "date"
        },
        "end_time": {
          "bsonType": "date"
        },
        "movie_id": {
          "bsonType": "objectId"
        },
        "movie_title": {
          "bsonType": "string"
        },
        "version_snapshot": {
          "bsonType": "object",
          "title": "object",
          "required": ["language", "subtitles", "format"],
          "properties": {
            "language": {
              "bsonType": "string"
            },
            "subtitles": {
              "bsonType": "string"
            },
            "format": {
              "bsonType": "string"
            }
          }  
        },
        "cinema_id": {
          "bsonType": "objectId"
        },
        "room_number": {
          "bsonType": "int"
        },
        "taken_seats": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["seat_number", "status"],
            "properties": {
              "seat_number": {
                "bsonType": "int"
              },
              "status": {
                "enum": ["reserved", "paid"]
              }
            }
          }  
        }
      }  
    } 
  }
});
//SCREENING

//SCREENING_ARCHIVE
db.createCollection("screening_archive", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "screening_archive",
      "required": ["cinema_id", "start_time", "end_time", "movie_id", "movie_title", "version_snapshot", "room_number"],
      "properties": {
        "start_time": {
          "bsonType": "date"
        },
        "end_time": {
          "bsonType": "date"
        },
        "movie_id": {
          "bsonType": "objectId"
        },
        "movie_title": {
          "bsonType": "string"
        },
        "version_snapshot": {
          "bsonType": "object",
          "title": "object",
          "required": ["language", "subtitles", "format"],
          "properties": {
            "language": {
              "bsonType": "string"
            },
            "subtitles": {
              "bsonType": "string"
            },
            "format": {
              "bsonType": "string"
            }
          }  
        },
        "cinema_id": {
          "bsonType": "objectId"
        },
        "room_number": {
          "bsonType": "int"
        },
        "taken_seats": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["seat_number", "status"],
            "properties": {
              "seat_number": {
                "bsonType": "int"
              },
              "status": {
                "enum": ["reserved", "paid"]
              }
            }
          }  
        }
      }  
    } 
  }
});
//SCREENING_ARCHIVE

//SHIFT
db.createCollection("shift", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "shift",
      "required": ["start_time", "end_time", "type", "worker_id", "cinema_id"],
      "properties": {
        "start_time": {
          "bsonType": "date"
        },
        "end_time": {
          "bsonType": "date"
        },
        "type": {
          "enum": ["cashier", "usher", "cleaner", "projection", "technical_support"]
        },
        "worker_id": {
          "bsonType": "objectId"
        },
        "cinema_id": {
          "bsonType": "objectId"
        }
      }  
    } 
  }
});
//SHIFT

//SPECIAL_OFFER
db.createCollection("special_offer", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "special_offer",
      "required": ["name", "start_time", "end_time", "amount"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "start_time": {
          "bsonType": "date"
        },
        "end_time": {
          "bsonType": "date"
        },
        "amount": {
          "bsonType": "int"
        }
      }  
    } 
  }
});
//SPECIAL_OFFER

//TICKET_TYPE
db.createCollection("ticket_type", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "ticket_type",
      "required": ["name", "base_price"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "base_price": {
          "bsonType": "decimal"
        }
      }  
    } 
  }
});
//TICKET_TYPE

//USER
db.createCollection("user", {
  validator: {
    $jsonSchema: {
      "bsonType": "object",
      "title": "user",
      "required": ["name", "surname", "birthdate", "username", "email", "password", "account_create_date", "type"],
      "properties": {
        "name": {
          "bsonType": "string"
        },
        "surname": {
          "bsonType": "string"
        },
        "birthdate": {
          "bsonType": "date"
        },
        "username": {
          "bsonType": "string"
        },
        "email": {
          "bsonType": "string"
        },
        "password": {
          "bsonType": "string"
        },
        "account_create_date": {
          "bsonType": "date"
        },
        "last_login_date": {
          "bsonType": "date"
        },
        "type": {
          "enum": ["service", "client", "supervisor", "regional_manager"]
        },
        "pesel_number": {
          "bsonType": "string"
        },
        "bank_account_number": {
          "bsonType": "string"
        },
        "salary_month": {
          "bsonType": "string"
        },
        "employments": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["start_date", "cinema_id"],
            "properties": {
              "start_date": {
                "bsonType": "date"
              },
              "end_date": {
                "bsonType": "date"
              },
              "cinema_id": {
                "bsonType": "objectId"
              }
            }
          }  
        },
        "terms": {
          "bsonType": "array",
          "items": {
            "title": "object",
            "required": ["start_date", "region_name"],
            "properties": {
              "start_date": {
                "bsonType": "date"
              },
              "end_date": {
                "bsonType": "date"
              },
              "region_name": {
                "bsonType": "string"
              }
            }
          }  
        }
      }  
    } 
  }
});
//USER