/** Map styles from interactivegooglemaps/static/js/interactivegooglemaps.js */
export const PLACES_MAP_STYLES: google.maps.MapTypeStyle[] = [
  {
    featureType: "all",
    elementType: "labels.text.fill",
    stylers: [{ saturation: 36 }, { color: "#9b9b9b" }, { lightness: 40 }],
  },
  {
    featureType: "all",
    elementType: "labels.text.stroke",
    stylers: [{ visibility: "off" }, { color: "#000000" }, { lightness: 16 }],
  },
  { featureType: "all", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
  {
    featureType: "administrative",
    elementType: "geometry.fill",
    stylers: [{ color: "#000000" }, { lightness: 20 }],
  },
  {
    featureType: "administrative",
    elementType: "geometry.stroke",
    stylers: [{ color: "#000000" }, { lightness: 17 }, { weight: 1.2 }],
  },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.fill",
    stylers: [{ color: "#00a0c4" }],
  },
  {
    featureType: "administrative.locality",
    elementType: "labels.text.stroke",
    stylers: [{ visibility: "off" }],
  },
  {
    featureType: "administrative.neighborhood",
    elementType: "labels.text.fill",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "landscape",
    elementType: "geometry",
    stylers: [{ color: "#232f3d" }, { lightness: "0" }],
  },
  {
    featureType: "poi",
    elementType: "geometry",
    stylers: [{ color: "#000000" }, { lightness: 21 }, { visibility: "off" }],
  },
  { featureType: "poi.park", elementType: "all", stylers: [{ visibility: "off" }] },
  { featureType: "poi.school", elementType: "all", stylers: [{ visibility: "off" }] },
  { featureType: "road", elementType: "all", stylers: [{ visibility: "on" }] },
  { featureType: "road", elementType: "geometry.fill", stylers: [{ color: "#ffffff" }] },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ lightness: "0" }, { color: "#ffffff" }, { visibility: "off" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry.fill",
    stylers: [{ color: "#000000" }, { lightness: "0" }, { visibility: "on" }],
  },
  {
    featureType: "road.highway",
    elementType: "geometry.stroke",
    stylers: [{ color: "#000000" }, { lightness: 29 }, { weight: 0.2 }],
  },
  {
    featureType: "road.highway",
    elementType: "labels.text.stroke",
    stylers: [{ visibility: "off" }],
  },
  { featureType: "road.highway", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
  { featureType: "road.arterial", elementType: "all", stylers: [{ visibility: "simplified" }] },
  {
    featureType: "road.arterial",
    elementType: "geometry",
    stylers: [{ color: "#000000" }, { lightness: "0" }],
  },
  {
    featureType: "road.arterial",
    elementType: "geometry.fill",
    stylers: [{ lightness: "0" }, { gamma: "1" }],
  },
  {
    featureType: "road.arterial",
    elementType: "labels.text.stroke",
    stylers: [{ visibility: "off" }],
  },
  { featureType: "road.local", elementType: "all", stylers: [{ visibility: "simplified" }] },
  {
    featureType: "road.local",
    elementType: "geometry",
    stylers: [{ color: "#000000" }, { lightness: 16 }],
  },
  {
    featureType: "transit",
    elementType: "geometry",
    stylers: [{ color: "#000000" }, { lightness: 19 }],
  },
  {
    featureType: "transit.line",
    elementType: "all",
    stylers: [{ visibility: "simplified" }, { weight: "3" }],
  },
  { featureType: "transit.line", elementType: "geometry", stylers: [{ visibility: "off" }] },
  {
    featureType: "transit.line",
    elementType: "geometry.fill",
    stylers: [{ visibility: "off" }, { color: "#ffb81c" }],
  },
  {
    featureType: "transit.line",
    elementType: "geometry.stroke",
    stylers: [{ visibility: "simplified" }],
  },
  { featureType: "transit.line", elementType: "labels", stylers: [{ weight: "1" }] },
  { featureType: "transit.line", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
  { featureType: "transit.station.airport", elementType: "all", stylers: [{ visibility: "off" }] },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#233f5b" }, { lightness: 17 }],
  },
];
